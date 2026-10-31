"""Milestone 1: understand one recording.

Prints recording information and annotations, then plots one hand-picked
rest -> foot-imagery example per run from the ORIGINAL (unprocessed) data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np

from eeg_rehab.config import PARTICIPANT, CHANNELS
from eeg_rehab.data import load_runs, print_recording_summary
from eeg_rehab.plotting import plot_rest_vs_imagery, to_uv

recordings = load_runs(PARTICIPANT)
print_recording_summary(recordings)

# Cue times verified from the annotations inspected above
cue_times = {
    6: 4.2,
    10: 12.5,
    14: 4.2,
}

# Observed spike in run 6 foot imagery (seconds within the segment)
highlight_spans = {
    6: (1.25, 1.5),
}

pairs = {}

for run_number, recording in recordings.items():
    sampling_rate = recording.info["sfreq"]
    cue = cue_times[run_number]

    rest_start = cue - 2
    rest_end = cue

    foot_start = cue + 1
    foot_end = cue + 3

    rest_data = recording.get_data(
        picks=CHANNELS,
        start=round(rest_start * sampling_rate),
        stop=round(rest_end * sampling_rate)
    )

    foot_data = recording.get_data(
        picks=CHANNELS,
        start=round(foot_start * sampling_rate),
        stop=round(foot_end * sampling_rate)
    )

    pairs[run_number] = {
        "rest": rest_data,
        "foot": foot_data,
        "sampling_rate": sampling_rate,
        "rest_start": rest_start,
        "rest_end": rest_end,
        "foot_start": foot_start,
        "foot_end": foot_end,
    }

    print(f"\nRun {run_number}")
    print(f"Rest: {rest_start:.1f}–{rest_end:.1f} s")
    print(f"Foot imagery: {foot_start:.1f}–{foot_end:.1f} s")
    print("Rest shape:", rest_data.shape)
    print("Foot imagery shape:", foot_data.shape)

# Set the same voltage scale for all comparison figures
largest_voltage = 0

for pair in pairs.values():
    for condition in ["rest", "foot"]:
        peak_voltage = np.max(np.abs(to_uv(pair[condition])))
        largest_voltage = max(largest_voltage, peak_voltage)

# Add some space above and below the largest voltage
voltage_limit = max(largest_voltage * 1.1, 1)

for run_number, pair in pairs.items():
    plot_rest_vs_imagery(
        pair, run_number, PARTICIPANT, voltage_limit,
        highlight_span=highlight_spans.get(run_number)
    )

plt.show()
