"""Load recordings and describe what they contain."""

import mne
from mne.datasets import eegbci

from .config import RUNS, REST_LABEL, HAND_LABEL, FOOT_LABEL


def load_runs(participant, runs=RUNS):
    """Download (if needed) and load each run. Returns {run_number: raw}."""
    recordings = {}
    for run_number in runs:
        files = eegbci.load_data(subjects=participant, runs=[run_number])
        recordings[run_number] = mne.io.read_raw_edf(files[0], preload=True)
    return recordings


def print_recording_summary(recordings):
    """Print sampling rate, channels, duration and every annotation."""
    for run_number, recording in recordings.items():
        print(f"\n========== RUN {run_number} ==========")
        print("Sampling rate:", recording.info["sfreq"], "Hz")
        print("Number of channels:", len(recording.ch_names))
        print(
            "Duration:",
            recording.n_times / recording.info["sfreq"],
            "seconds"
        )

        labels = recording.annotations.description

        print("Rest periods:", sum(labels == REST_LABEL))
        print("Hand-imagery periods:", sum(labels == HAND_LABEL))
        print("Foot-imagery periods:", sum(labels == FOOT_LABEL))

        print("\nStart (s) | Duration (s) | Label")

        for start, duration, label in zip(
            recording.annotations.onset,
            recording.annotations.duration,
            recording.annotations.description
        ):
            print(f"{start:8.1f} | {duration:12.1f} | {label}")
