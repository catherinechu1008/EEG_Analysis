"""Merge hand-entered quality review notes into the trial table.

Review judgments live in data/quality_review.csv, one row per reviewed trial,
so they stay traceable and extend to new participants without code changes.
Trials missing from that file keep quality_status "not reviewed".
"""

import csv

from .config import QUALITY_REVIEW_CSV


def load_quality_review(review_csv=QUALITY_REVIEW_CSV):
    """Return {(participant, run, trial): review row}."""
    reviews = {}
    with open(review_csv, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            key = (int(row["participant"]), int(row["run"]), int(row["trial"]))
            reviews[key] = row
    return reviews


def apply_quality_review(trial_table, review_csv=QUALITY_REVIEW_CSV):
    """Add quality_status, quality_note and include to reviewed trials."""
    reviews = load_quality_review(review_csv)
    for row in trial_table:
        if row["extraction_status"] != "extracted":
            continue
        review = reviews.get((row["participant"], row["run"], row["trial"]))
        if review is None:
            continue
        row["quality_status"] = review["quality_status"]
        row["quality_note"] = review["quality_note"]
        row["include"] = review["include"].strip().lower() == "true"


def print_quality_summary(trial_table):
    """Print how many extracted trials were reviewed, flagged and included."""
    extracted = [r for r in trial_table if r["extraction_status"] == "extracted"]
    unreviewed = [r for r in extracted if r["quality_status"] == "not reviewed"]
    flagged = [r for r in extracted if r["quality_status"] == "flagged for review"]
    included = [r for r in extracted if r.get("include")]

    print("\nQUALITY REVIEW SUMMARY")
    print(f"Reviewed: {len(extracted) - len(unreviewed)}/{len(extracted)}")
    print(f"Flagged for review: {len(flagged)}")
    for row in flagged:
        print(f"    Run {row['run']} trial {row['trial']}: {row['quality_note']}")
    print(f"Included: {len(included)}/{len(extracted)}")
