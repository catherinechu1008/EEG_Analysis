import sys
import csv
from pathlib import Path

import numpy as np
import mne

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeg_rehab.config import CHANNELS, PRIMARY_CHANNEL, VOLTS_TO_UV, OUTPUT_DIR
from eeg_rehab.pipeline import prepare_participant

mne.set_log_level("WARNING")

PARTICIPANTS = [1, 33, 14, 79, 98]
EXPECTED_SFREQ = 160
FIXED_LIMIT_UV = 150
RELATIVE_FACTOR = 3

ch = CHANNELS.index(PRIMARY_CHANNEL)
flag_rows = []
summary = []

for pid in PARTICIPANTS:
    try:
        trial_pairs, trial_table = prepare_participant(pid)
    except Exception as error:
        print(f"Participant {pid}: FORMAT PROBLEM -> {error}")
        summary.append((pid, "format problem", 0, 0, 0, 0))
        continue

    sfreqs = {pair["sampling_rate"] for pair in trial_pairs}
    if sfreqs != {EXPECTED_SFREQ}:
        print(f"Participant {pid}: FORMAT PROBLEM -> sampling rate {sfreqs}")
        summary.append((pid, f"sampling rate {sfreqs}", 0, 0, 0, 0))
        continue

    rest_p2p = np.array([np.ptp(p["rest"][ch]) for p in trial_pairs]) * VOLTS_TO_UV
    foot_p2p = np.array([np.ptp(p["foot"][ch]) for p in trial_pairs]) * VOLTS_TO_UV
    trial_p2p = np.maximum(rest_p2p, foot_p2p) 

    fixed_flag = trial_p2p > FIXED_LIMIT_UV 
    relative_limit = RELATIVE_FACTOR * np.median(trial_p2p)
    relative_flag = trial_p2p > relative_limit

    for pair, r, f, t, ff, rf in zip(trial_pairs, rest_p2p, foot_p2p,
                                     trial_p2p, fixed_flag, relative_flag):
        flag_rows.append({
            "participant": pid, "run": pair["run"], "trial": pair["trial"],
            "rest_p2p_uv": round(r, 1), "foot_p2p_uv": round(f, 1),
            "fixed_flag": bool(ff), "relative_flag": bool(rf),
        })

    n_skipped = sum(r["extraction_status"] == "skipped" for r in trial_table)
    summary.append((pid, "ok", len(trial_pairs), n_skipped,
                    fixed_flag.sum(), relative_flag.sum()))
    print(f"Participant {pid}: median peak-to-peak {np.median(trial_p2p):.0f} µV, "
          f"relative limit {relative_limit:.0f} µV")

print("\nSTEP 3a SUMMARY (no mu/beta results computed)")
print("Participant  Format          Extracted  Skipped  Fixed flags  Relative flags")
for pid, status, n, skipped, nf, nr in summary:
    print(f"{pid:>11}  {status:<14}  {n:>9}  {skipped:>7}  {nf:>11}  {nr:>14}")

path = OUTPUT_DIR / "m5_quality_flags.csv"
path.parent.mkdir(parents=True, exist_ok=True)
with open(path, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=list(flag_rows[0]))
    writer.writeheader()
    writer.writerows(flag_rows)
print("Saved", path)

    