"""Milestone 5, step 1: choose participants BEFORE viewing any of their data.

Participant 1 is kept. The other four come from a seeded shuffle of 2-109.
The full shuffled order is saved so any replacement (for data-format reasons
only, never for results) is decided in advance: take the next ID in order.
"""

import sys
import csv
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeg_rehab.config import DATA_DIR

SEED = 2026          # written down before running; do not change afterwards
N_EXTRA = 4

rng = np.random.default_rng(SEED)
order = rng.permutation(np.arange(2, 110)).tolist()

chosen = [1] + order[:N_EXTRA]
backups = order[N_EXTRA:]

print(f"Seed {SEED}")
print(f"Chosen participants: {chosen}")
print(f"Next backups in order: {backups[:5]} ...")

path = DATA_DIR / "participant_selection.csv"
with open(path, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["position", "participant", "role"])
    writer.writerow([0, 1, "chosen (starting participant)"])
    for i, pid in enumerate(order, start=1):
        role = "chosen" if i <= N_EXTRA else "backup"
        writer.writerow([i, pid, role])
print("Saved", path)
