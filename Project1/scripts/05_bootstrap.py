"""Milestone 5, step 5: bootstrap uncertainty for each participant.

Resamples whole trials (never time slices) with replacement, using the
step 3b per-trial mu changes with all trials kept.
"""

import sys
import csv
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeg_rehab.config import OUTPUT_DIR

PARTICIPANTS = [1, 33, 14, 79, 98]
N_BOOT = 10_000
SEED = 2026

rng = np.random.default_rng(SEED)

with open(OUTPUT_DIR / "m5_trial_changes.csv", newline="", encoding="utf-8") as file:
    changes = list(csv.DictReader(file))

print(f"STEP 5: bootstrap 95% intervals, {N_BOOT} resamples of whole trials "
      f"(seed {SEED})")
print("Participant  Trials  Mean mu dB   95% interval      % lower   95% interval")
for pid in PARTICIPANTS:
    mu = np.array([float(r["mu_change_db"]) for r in changes
                   if int(r["participant"]) == pid])
    n = len(mu)

    picks = rng.integers(0, n, size=(N_BOOT, n))   # each row: one pretend set
    resampled = mu[picks]                          # (N_BOOT, n) mu values
    boot_mean = resampled.mean(axis=1)
    boot_pct_lower = (resampled < 0).mean(axis=1) * 100

    mean_lo, mean_hi = np.percentile(boot_mean, [2.5, 97.5])
    pct_lo, pct_hi = np.percentile(boot_pct_lower, [2.5, 97.5])
    print(f"{pid:>11}  {n:>6}  {mu.mean():>+10.2f}  {mean_lo:+6.2f} to {mean_hi:+6.2f}"
          f"  {(mu < 0).mean() * 100:>7.0f}%  {pct_lo:4.0f}% to {pct_hi:3.0f}%")
