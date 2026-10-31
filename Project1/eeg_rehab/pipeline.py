"""Run the full Milestone 2 pipeline for one participant without plots.

Later milestones start here instead of repeating loading, filtering,
referencing and extraction.
"""

from .config import RUNS, QUALITY_REVIEW_CSV
from .data import load_runs
from .preprocessing import preprocess_runs
from .quality import apply_quality_review
from .trials import extract_trials


def prepare_participant(participant, runs=RUNS, review_csv=QUALITY_REVIEW_CSV):
    """Return (trial_pairs, trial_table) for one participant."""
    recordings = load_runs(participant, runs)
    _, referenced_runs = preprocess_runs(recordings)
    trial_pairs, trial_table = extract_trials(referenced_runs, participant)
    apply_quality_review(trial_table, review_csv)
    return trial_pairs, trial_table
