"""Milestone 5, step 4: do the results change without flagged trials?

Combines step 3a flags with step 3b per-trial changes; no EEG reprocessing.
"""

import sys
import csv
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeg_rehab.config import OUTPUT_DIR

PARTICIPANTS = [1, 33, 14, 79, 98]
VISUAL_FLAGS_P1 = {(10, 1), (14, 8)}   # Milestone 2 visual review


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def summary(mu):
    mu = np.array(mu)
    return f"{(mu < 0).sum():>2}/{len(mu):<2} lower, mean {mu.mean():+.2f} dB"


changes = read_csv(OUTPUT_DIR / "m5_trial_changes.csv")
fixed_flag = {
    (int(r["participant"]), int(r["run"]), int(r["trial"])): r["fixed_flag"] == "True"
    for r in read_csv(OUTPUT_DIR / "m5_quality_flags.csv")
}

print("STEP 4: Cz mu change, all trials vs without fixed-rule (150 µV) flags")
for pid in PARTICIPANTS:
    rows = [r for r in changes if int(r["participant"]) == pid]
    mu_all = [float(r["mu_change_db"]) for r in rows]
    mu_kept = [float(r["mu_change_db"]) for r in rows
               if not fixed_flag[(pid, int(r["run"]), int(r["trial"]))]]
    print(f"P{pid:<3} all: {summary(mu_all)}   without flags: {summary(mu_kept)}")

p1_rows = [r for r in changes if int(r["participant"]) == 1]
p1_kept = [float(r["mu_change_db"]) for r in p1_rows
           if (int(r["run"]), int(r["trial"])) not in VISUAL_FLAGS_P1]
print(f"\nP1 without Milestone 2 visual flags (run 10 trial 1, "
      f"run 14 trial 8): {summary(p1_kept)}")
