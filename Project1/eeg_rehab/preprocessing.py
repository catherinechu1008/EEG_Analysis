"""Filtering and referencing. Original recordings are never modified."""

from .config import L_FREQ, H_FREQ


def preprocess(raw):
    """Return (filtered, referenced) copies of one recording.

    Filter 1–40 Hz to retain the target mu (8–13 Hz) and beta (13–30 Hz)
    bands. This wider filter also reduces slow drift and higher-frequency
    fluctuations. Zero phase uses future samples, so this is offline only.
    """
    filtered = raw.copy()
    filtered.filter(
        l_freq=L_FREQ,
        h_freq=H_FREQ,
        method="fir",
        phase="zero"
    )

    referenced = filtered.copy()
    referenced.set_eeg_reference(
        ref_channels="average",
        projection=False
    )

    return filtered, referenced


def preprocess_runs(recordings):
    """Preprocess every run. Returns ({run: filtered}, {run: referenced})."""
    filtered_runs = {}
    referenced_runs = {}
    for run_number, raw in recordings.items():
        filtered_runs[run_number], referenced_runs[run_number] = preprocess(raw)
    return filtered_runs, referenced_runs
