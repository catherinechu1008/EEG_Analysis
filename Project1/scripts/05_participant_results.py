"""Milestone 5, step 3b: frozen Milestone 4 analysis on all five participants.

Settings are unchanged from Milestone 4. All trials are kept here; the
without-flagged-trials comparison is a separate step.
"""

import sys
import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import mne
from scipy.signal import spectrogram

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeg_rehab.config import (
    PRIMARY_CHANNEL, VOLTS_TO_UV, EPOCH_WINDOW, MU_BAND, BETA_BAND, OUTPUT_DIR,
)
from eeg_rehab.data import load_runs
from eeg_rehab.preprocessing import preprocess_runs
from eeg_rehab.trials import extract_trials

mne.set_log_level("WARNING")

PARTICIPANTS = [1, 33, 14, 79, 98]

# Frozen Milestone 4 settings: do not change
WINDOW_SECONDS = 1.0
STEP_SECONDS = 0.1
BASELINE_CENTRES = (-1.5, -0.5)   # slices fully inside rest (-2 to 0 s)
IMAGERY_CENTRES = (1.5, 2.5)      # slices fully inside imagery (1 to 3 s)


def cut_epochs(referenced_runs, trial_table):
    """Cue-aligned Cz epochs (-2 to +4 s) for every extracted trial, in µV."""
    epochs, keys = [], []
    for row in trial_table:
        if row["extraction_status"] != "extracted":
            continue
        recording = referenced_runs[row["run"]]
        sfreq = recording.info["sfreq"]
        n_samples = round((EPOCH_WINDOW[1] - EPOCH_WINDOW[0]) * sfreq)
        start = round((row["cue_s"] + EPOCH_WINDOW[0]) * sfreq)
        epoch = recording.get_data(picks=PRIMARY_CHANNEL, start=start,
                                   stop=start + n_samples)[0]
        if len(epoch) != n_samples:
            raise ValueError(f"Run {row['run']} trial {row['trial']}: "
                             f"epoch runs past the end of the recording")
        epochs.append(epoch * VOLTS_TO_UV)
        keys.append((row["run"], row["trial"]))
    return np.array(epochs), keys, sfreq


def analyse(epochs, sfreq):
    """Per-trial raw-first band changes and the ratio-averaged change map."""
    nperseg = round(WINDOW_SECONDS * sfreq)
    noverlap = nperseg - round(STEP_SECONDS * sfreq)
    freqs, times, power = spectrogram(
        epochs, fs=sfreq, window="hann", nperseg=nperseg,
        noverlap=noverlap, scaling="density", mode="psd", axis=-1,
    )                                   # power: (trials, frequencies, times)
    centres = np.round(times + EPOCH_WINDOW[0], 6)
    in_base = (centres >= BASELINE_CENTRES[0]) & (centres <= BASELINE_CENTRES[1])
    in_task = (centres >= IMAGERY_CENTRES[0]) & (centres <= IMAGERY_CENTRES[1])

    # Primary number: average raw power first, then compare with rest once
    changes = {}
    for name, band in (("mu", MU_BAND), ("beta", BETA_BAND)):
        rows = (freqs >= band[0]) & (freqs <= band[1])
        rest = power[:, rows][:, :, in_base].mean(axis=(1, 2))
        task = power[:, rows][:, :, in_task].mean(axis=(1, 2))
        changes[name] = 10 * np.log10(task / rest)

    # Primary display: per-trial ratios to own rest, averaged, then dB
    trial_base = power[:, :, in_base].mean(axis=2, keepdims=True)
    mean_ratio_db = 10 * np.log10((power / trial_base).mean(axis=0))
    in_mu = (freqs >= MU_BAND[0]) & (freqs <= MU_BAND[1])
    map_mu = mean_ratio_db[in_mu][:, in_task].mean()

    return freqs, centres, mean_ratio_db, changes, map_mu


results = {}
trial_rows = []
for pid in PARTICIPANTS:
    recordings = load_runs(pid)
    _, referenced_runs = preprocess_runs(recordings)
    _, trial_table = extract_trials(referenced_runs, pid)
    epochs, keys, sfreq = cut_epochs(referenced_runs, trial_table)

    freqs, centres, mean_ratio_db, changes, map_mu = analyse(epochs, sfreq)
    results[pid] = (freqs, centres, mean_ratio_db, changes, map_mu)

    for (run, trial), mu, beta in zip(keys, changes["mu"], changes["beta"]):
        trial_rows.append({"participant": pid, "run": run, "trial": trial,
                           "mu_change_db": round(mu, 3),
                           "beta_change_db": round(beta, 3)})
    print(f"Participant {pid}: done ({len(epochs)} trials)")

print("\nSTEP 3b SUMMARY: Cz, imagery 1-3 s vs rest -2-0 s, all trials kept")
print("Participant  Trials  Mu lower  Mu mean dB  Map mu dB  Beta lower  Beta mean dB")
for pid, (_, _, _, changes, map_mu) in results.items():
    mu, beta = changes["mu"], changes["beta"]
    n = len(mu)
    print(f"{pid:>11}  {n:>6}  {(mu < 0).sum():>4}/{n:<3}  {mu.mean():>+10.2f}"
          f"  {map_mu:>+9.2f}  {(beta < 0).sum():>6}/{n:<3}  {beta.mean():>+12.2f}")

print("\nSanity check, participant 1 should match Milestone 4: "
      "mu lower 7/24, mean +0.94 dB, map +2.07 dB")

path = OUTPUT_DIR / "m5_trial_changes.csv"
with open(path, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=list(trial_rows[0]))
    writer.writeheader()
    writer.writerows(trial_rows)
print("Saved", path)

# One change map per participant, same colour scale for all
fig, axes = plt.subplots(1, len(PARTICIPANTS), figsize=(18, 4), sharey=True,
                         layout="constrained")
for ax, (pid, (freqs, centres, mean_ratio_db, changes, map_mu)) in zip(
        axes, results.items()):
    shown = (freqs >= 1) & (freqs <= 40)
    mesh = ax.pcolormesh(centres, freqs[shown], mean_ratio_db[shown],
                         shading="nearest", cmap="RdBu_r", vmin=-3, vmax=3)
    ax.axvline(0, color="black", lw=1.5)
    for t in BASELINE_CENTRES:
        ax.axvline(t, color="grey", lw=1, ls=":")
    for t in IMAGERY_CENTRES:
        ax.axvline(t, color="tab:orange", lw=1, ls=":")
    for f in (8, 13, 30):
        ax.axhline(f, color="black", lw=0.6, ls="--")
    mu = changes["mu"]
    ax.set_title(f"P{pid}: mu lower {(mu < 0).sum()}/{len(mu)}\n"
                 f"map mu {map_mu:+.2f} dB")
    ax.set_xlabel("Time relative to cue (s)")
axes[0].set_ylabel("Frequency (Hz)")
fig.colorbar(mesh, ax=axes, label="Change from rest (dB)")
fig.suptitle("Cz change from rest, ratio-averaged across trials "
             "(frozen Milestone 4 settings)")
plt.show()
