"""Milestone 2: prepare trustworthy comparisons.

Filters and average-references every run, shows before/after inspection
plots, extracts matched rest / foot-imagery pairs, merges the quality review
from data/quality_review.csv, and saves outputs/trial_table.csv.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from eeg_rehab.config import PARTICIPANT, TRIAL_TABLE_CSV
from eeg_rehab.data import load_runs
from eeg_rehab.preprocessing import preprocess_runs
from eeg_rehab.quality import apply_quality_review, print_quality_summary
from eeg_rehab.trials import (
    extract_trials, print_extraction_summary, save_trial_table,
)
from eeg_rehab.plotting import (
    plot_filter_comparison, plot_reference_comparison, plot_trial_grid,
)

# Set to False to run the pipeline without opening figures
SHOW_PLOTS = True

# First foot-imagery cue in each run, used for the inspection plots
example_cues = {
    6: 4.2,
    10: 12.5,
    14: 4.2,
}

recordings = load_runs(PARTICIPANT)
filtered_runs, referenced_runs = preprocess_runs(recordings)

if SHOW_PLOTS:
    # Original vs filtered Cz, run 6, two seconds before to three after cue
    cue = example_cues[6]
    plot_filter_comparison(
        recordings[6], filtered_runs[6], 6,
        start_s=cue - 2, stop_s=cue + 3, cue=cue
    )

    # Scroll through the middle 16 channels of filtered run 6
    channels_to_check = filtered_runs[6].ch_names[16:32]
    filtered_runs[6].plot(
        picks=channels_to_check,
        n_channels=16,
        start=0,
        duration=10,
        scalings={"eeg": 100e-6}
    )

    # Compare Cz before and after average referencing for each run.
    for run_number, cue in example_cues.items():
        plot_reference_comparison(
            filtered_runs[run_number], referenced_runs[run_number],
            run_number, PARTICIPANT, cue
        )

trial_pairs, trial_table = extract_trials(referenced_runs, PARTICIPANT)
apply_quality_review(trial_table)

print_extraction_summary(trial_table, trial_pairs)
print_quality_summary(trial_table)

save_trial_table(trial_table, TRIAL_TABLE_CSV)

if SHOW_PLOTS:
    for run_number in referenced_runs:
        plot_trial_grid(trial_pairs, run_number)

    plt.show()
