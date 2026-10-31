"""Reusable figures. Each function draws one figure and returns it.

Data stay in volts everywhere else; conversion to microvolts happens here.
Figures are shown with plt.show(block=False); call plt.show() once at the
end of a script to keep the windows open.
"""

import matplotlib.pyplot as plt
import numpy as np

from .config import (
    CHANNEL_LABELS, PRIMARY_CHANNEL, REST_WINDOW, IMAGERY_WINDOW, VOLTS_TO_UV,
)


def to_uv(data):
    """Convert EEG from volts to microvolts."""
    return data * VOLTS_TO_UV


def plot_rest_vs_imagery(pair, run_number, participant, voltage_limit,
                         highlight_span=None):
    """Rows = C3, Cz, C4. Left column = rest, right column = foot imagery.

    highlight_span: optional (start, end) in seconds within the imagery
    segment to shade, e.g. an observed spike.
    """
    fig, axes = plt.subplots(
        3, 2,
        figsize=(12, 7),
        sharex=True,
        sharey=True
    )

    fig.suptitle(
        f"Participant {participant} · Run {run_number} · Rest vs foot imagery",
        fontsize=15
    )

    for row in range(3):
        rest_uv = to_uv(pair["rest"][row])
        foot_uv = to_uv(pair["foot"][row])

        rest_times = np.arange(len(rest_uv)) / pair["sampling_rate"]
        foot_times = np.arange(len(foot_uv)) / pair["sampling_rate"]

        # Left column: rest
        axes[row, 0].plot(
            rest_times,
            rest_uv,
            color="steelblue",
            linewidth=0.9
        )

        # Right column: foot imagery
        axes[row, 1].plot(
            foot_times,
            foot_uv,
            color="darkorange",
            linewidth=0.9
        )

        axes[row, 0].set_ylabel(
            f"{CHANNEL_LABELS[row]}\nVoltage (µV)"
        )

        for column in range(2):
            axes[row, column].set_xlim(0, 2)
            axes[row, column].set_ylim(
                -voltage_limit, voltage_limit
            )
            axes[row, column].grid(alpha=0.2)

        if highlight_span is not None:
            axes[row, 1].axvspan(
                *highlight_span,
                color="orange",
                alpha=0.18
            )

    axes[0, 0].set_title(
        f"Rest\n"
        f"Recording time "
        f"{pair['rest_start']:.1f}–{pair['rest_end']:.1f} s"
    )

    axes[0, 1].set_title(
        f"Foot imagery\n"
        f"Recording time "
        f"{pair['foot_start']:.1f}–{pair['foot_end']:.1f} s"
    )

    axes[2, 0].set_xlabel("Time within segment (seconds)")
    axes[2, 1].set_xlabel("Time within segment (seconds)")

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.show(block=False)
    return fig


def plot_filter_comparison(raw, filtered, run_number, start_s, stop_s, cue,
                           channel=PRIMARY_CHANNEL, title_suffix="1–40 Hz"):
    """Original vs filtered signal for one channel over the same interval."""
    sampling_rate = raw.info["sfreq"]
    start_sample = round(start_s * sampling_rate)
    stop_sample = round(stop_s * sampling_rate)

    original = to_uv(raw.get_data(
        picks=[channel], start=start_sample, stop=stop_sample
    )[0])
    filtered_uv = to_uv(filtered.get_data(
        picks=[channel], start=start_sample, stop=stop_sample
    )[0])

    # Recording times for the horizontal axis
    times = start_s + np.arange(len(original)) / sampling_rate
    label = channel.rstrip(".")

    fig, axes = plt.subplots(
        2, 1, figsize=(12, 6), sharex=True, sharey=True
    )

    axes[0].plot(times, original, color="gray", linewidth=0.9)
    axes[0].set_title(f"Original {label}")

    axes[1].plot(times, filtered_uv, color="steelblue", linewidth=0.9)
    axes[1].set_title(f"Filtered {label} · {title_suffix}")

    for ax in axes:
        ax.set_ylabel("Voltage (µV)")
        ax.axvline(cue, color="darkorange", linestyle="--")
        ax.grid(alpha=0.2)

    axes[1].set_xlabel("Recording time (seconds)")
    fig.suptitle(f"Run {run_number} · Before and after filtering")
    plt.tight_layout()
    plt.show(block=False)
    return fig


def plot_reference_comparison(before_recording, after_recording, run_number,
                              participant, cue, channel=PRIMARY_CHANNEL):
    """One channel before and after average referencing around one cue."""
    sampling_rate = before_recording.info["sfreq"]
    label = channel.rstrip(".")

    # Display from two seconds before the cue to three seconds after it.
    start_sample = round((cue + REST_WINDOW[0]) * sampling_rate)
    stop_sample = round((cue + IMAGERY_WINDOW[1]) * sampling_rate)

    before = to_uv(before_recording.get_data(
        picks=[channel], start=start_sample, stop=stop_sample
    )[0])
    after = to_uv(after_recording.get_data(
        picks=[channel], start=start_sample, stop=stop_sample
    )[0])

    # Convert sample positions to times in the full recording.
    times = (start_sample + np.arange(len(before))) / sampling_rate

    fig, axes = plt.subplots(
        2, 1, figsize=(12, 6), sharex=True, sharey=True
    )

    axes[0].plot(times, before, color="gray", linewidth=0.9)
    axes[0].set_title(f"Filtered {label} | Before average referencing")

    axes[1].plot(times, after, color="steelblue", linewidth=0.9)
    axes[1].set_title(f"Filtered {label} | After average referencing")

    for ax in axes:
        ax.axvspan(cue + REST_WINDOW[0], cue + REST_WINDOW[1],
                   color="steelblue", alpha=0.08,
                   label="Selected rest window")
        ax.axvspan(cue + IMAGERY_WINDOW[0], cue + IMAGERY_WINDOW[1],
                   color="darkorange", alpha=0.08,
                   label="Selected imagery window")
        ax.axvline(cue, color="darkorange", linestyle="--",
                   label="Foot-imagery cue")
        ax.set_ylabel("Voltage (µV)")
        ax.set_xlim(start_sample / sampling_rate, stop_sample / sampling_rate)
        ax.grid(alpha=0.2)

    axes[0].legend(loc="upper right", fontsize=8)
    axes[1].set_xlabel("Recording time (seconds)")
    fig.suptitle(
        f"Participant {participant} | Run {run_number} | "
        f"Effect of average referencing"
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show(block=False)
    return fig


def plot_trial_grid(trial_pairs, run_number, channel=PRIMARY_CHANNEL):
    """Every extracted pair from one run: rest on the left, imagery right."""
    run_pairs = [
        pair for pair in trial_pairs
        if pair["run"] == run_number
    ]
    label = channel.rstrip(".")

    fig, axes = plt.subplots(
        len(run_pairs), 2,
        figsize=(12, 2 * len(run_pairs)),
        sharex=True,
        sharey=True,
        squeeze=False
    )

    for row, pair in enumerate(run_pairs):
        channel_index = pair["channels"].index(channel)
        times = np.arange(pair["rest"].shape[1]) / pair["sampling_rate"]

        for column, condition in enumerate(["rest", "foot"]):
            voltage = to_uv(pair[condition][channel_index])

            axes[row, column].plot(times, voltage, linewidth=0.8)
            axes[row, column].grid(alpha=0.2)

        axes[row, 0].set_ylabel(
            f"Trial {pair['trial']}\nµV"
        )

    axes[0, 0].set_title("Rest")
    axes[0, 1].set_title("Foot imagery")

    for ax in axes[-1]:
        ax.set_xlabel("Time within segment (seconds)")

    fig.suptitle(f"Run {run_number} · All extracted {label} pairs")
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show(block=False)
    return fig
