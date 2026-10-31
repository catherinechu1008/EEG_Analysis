"""Cut matched rest and foot-imagery segments around each T2 cue."""

import csv

import numpy as np

from .config import (
    CHANNELS, TASK_LABELS, REST_LABEL, FOOT_LABEL,
    REST_WINDOW, IMAGERY_WINDOW,
)


def window_has_condition(start, stop, wanted_label, task_annotations):
    """Check full coverage, rejecting gaps and conflicting task labels."""
    covered_until = start
    tolerance = 1e-8
    for onset, end, label in task_annotations:
        if end <= start + tolerance or onset >= stop - tolerance:
            continue
        if label != wanted_label:
            return False
        if onset > covered_until + tolerance:
            return False
        covered_until = max(covered_until, end)
    return covered_until >= stop - tolerance


def get_task_annotations(recording):
    """Return sorted (onset, end, label) in seconds from the recording start."""
    return sorted([
        (float(onset - recording.first_time),
         float(onset - recording.first_time + duration), str(label))
        for onset, duration, label in zip(
            recording.annotations.onset,
            recording.annotations.duration,
            recording.annotations.description
        )
        if label in TASK_LABELS
    ])


def extract_trials(recordings, participant, channels=CHANNELS):
    """Extract every eligible T2 cue from processed recordings.

    Returns (trial_pairs, trial_table):
      trial_pairs: EEG arrays for extracted pairs, in volts
      trial_table: one record per T2 cue, including skipped cues and reasons
    """
    trial_pairs = []
    trial_table = []

    for run_number, recording in recordings.items():
        sfreq = recording.info["sfreq"]
        rest_samples = round((REST_WINDOW[1] - REST_WINDOW[0]) * sfreq)
        foot_samples = round((IMAGERY_WINDOW[1] - IMAGERY_WINDOW[0]) * sfreq)
        recording_end = recording.n_times / sfreq
        task_annotations = get_task_annotations(recording)

        trial_number = 0
        for cue, task_end, label in task_annotations:
            if label != FOOT_LABEL:
                continue
            trial_number += 1

            # Round starts to actual samples; take exactly the window length.
            rest_sample = round((cue + REST_WINDOW[0]) * sfreq)
            foot_sample = round((cue + IMAGERY_WINDOW[0]) * sfreq)
            rest_start = rest_sample / sfreq
            rest_end = (rest_sample + rest_samples) / sfreq
            foot_start = foot_sample / sfreq
            foot_end = (foot_sample + foot_samples) / sfreq

            reasons = []
            if rest_start < 0 or foot_end > recording_end:
                reasons.append("window outside recording")
            if not window_has_condition(
                    rest_start, rest_end, REST_LABEL, task_annotations):
                reasons.append("rest window not fully within T0")
            if not window_has_condition(
                    foot_start, foot_end, FOOT_LABEL, task_annotations):
                reasons.append("imagery window not fully within T2")

            record = {
                "participant": participant, "run": run_number,
                "trial": trial_number, "cue_s": cue,
                "rest_start_s": rest_start, "rest_end_s": rest_end,
                "foot_start_s": foot_start, "foot_end_s": foot_end,
                "rest_label": REST_LABEL, "foot_label": FOOT_LABEL,
                "quality_status": "not reviewed",
            }

            if not reasons:
                rest_eeg = recording.get_data(
                    picks=channels, start=rest_sample,
                    stop=rest_sample + rest_samples
                )
                foot_eeg = recording.get_data(
                    picks=channels, start=foot_sample,
                    stop=foot_sample + foot_samples
                )
                if (rest_eeg.shape != (len(channels), rest_samples)
                        or foot_eeg.shape != (len(channels), foot_samples)):
                    reasons.append("unexpected segment shape")
                elif not (np.isfinite(rest_eeg).all()
                          and np.isfinite(foot_eeg).all()):
                    reasons.append("non-finite EEG measurements")
                else:
                    trial_pairs.append({
                        "participant": participant, "run": run_number,
                        "trial": trial_number, "cue_s": cue,
                        "channels": list(channels), "sampling_rate": sfreq,
                        "rest": rest_eeg, "foot": foot_eeg,
                    })

            record["extraction_status"] = "skipped" if reasons else "extracted"
            record["exclusion_reason"] = "; ".join(reasons)
            trial_table.append(record)

    return trial_pairs, trial_table


def print_extraction_summary(trial_table, trial_pairs):
    """Print every T2 cue with its windows and status, then per-run counts."""
    print("\nALL FOOT-IMAGERY CUES: EXTRACTION SUMMARY")
    print("Run Trial   Cue(s)     Rest window(s)    Imagery window(s)   Status")
    for row in trial_table:
        print(
            f"{row['run']:3d} {row['trial']:5d} {row['cue_s']:8.2f}"
            f"  {row['rest_start_s']:7.2f}–{row['rest_end_s']:6.2f}"
            f"  {row['foot_start_s']:7.2f}–{row['foot_end_s']:6.2f}"
            f"   {row['extraction_status']}"
        )
        if row["exclusion_reason"]:
            print("    Reason:", row["exclusion_reason"])

    for run_number in dict.fromkeys(row["run"] for row in trial_table):
        rows = [r for r in trial_table if r["run"] == run_number]
        kept = sum(r["extraction_status"] == "extracted" for r in rows)
        print(f"Run {run_number}: {kept}/{len(rows)} pairs extracted")

    print("Total extracted pairs:", len(trial_pairs))


def save_trial_table(trial_table, path):
    """Write the trial table to CSV, including notes added during review."""
    columns = list(dict.fromkeys(
        key for row in trial_table for key in row
    ))

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(trial_table)

    print("Saved", path)
