"""Milestone 5, step 6: participant-level summary and comparison figure.

Each participant is reduced to one number before any between-person
summary, so each brain counts once however many trials it has.
"""

import sys
import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeg_rehab.config import OUTPUT_DIR

PARTICIPANTS = [1, 33, 14, 79, 98]
N_BOOT = 10_000
SEED = 2026

rng = np.random.default_rng(SEED)

with open(OUTPUT_DIR / "m5_trial_changes.csv", newline="", encoding="utf-8") as file:
    changes = list(csv.DictReader(file))

# Within each person: resample that person's trials (same as step 5)
person = {}
for pid in PARTICIPANTS:
    mu = np.array([float(r["mu_change_db"]) for r in changes
                   if int(r["participant"]) == pid])
    resampled = mu[rng.integers(0, len(mu), size=(N_BOOT, len(mu)))]
    person[pid] = {
        "n": len(mu),
        "mean": mu.mean(),
        "mean_ci": np.percentile(resampled.mean(axis=1), [2.5, 97.5]),
        "pct": (mu < 0).mean() * 100,
        "pct_ci": np.percentile((resampled < 0).mean(axis=1) * 100, [2.5, 97.5]),
    }

# Between people: one number per person, then resample the 5 PEOPLE
person_means = np.array([person[p]["mean"] for p in PARTICIPANTS])
person_pcts = np.array([person[p]["pct"] for p in PARTICIPANTS])
people = rng.integers(0, len(PARTICIPANTS), size=(N_BOOT, len(PARTICIPANTS)))
group = {
    "mean": person_means.mean(),
    "mean_ci": np.percentile(person_means[people].mean(axis=1), [2.5, 97.5]),
    "pct": person_pcts.mean(),
    "pct_ci": np.percentile(person_pcts[people].mean(axis=1), [2.5, 97.5]),
}
n_down = (person_means < 0).sum()

print("STEP 6: participant-level summary (each person counts once)")
for pid in PARTICIPANTS:
    p = person[pid]
    print(f"  P{pid:<3} mean {p['mean']:+.2f} dB "
          f"[{p['mean_ci'][0]:+.2f}, {p['mean_ci'][1]:+.2f}], "
          f"{p['pct']:.0f}% lower [{p['pct_ci'][0]:.0f}, {p['pct_ci'][1]:.0f}]")
print(f"Across people: {n_down} of {len(PARTICIPANTS)} went down on average")
print(f"  Average of person means {group['mean']:+.2f} dB "
      f"[{group['mean_ci'][0]:+.2f}, {group['mean_ci'][1]:+.2f}]  (rough: n = 5)")
print(f"  Average of person % lower {group['pct']:.0f}% "
      f"[{group['pct_ci'][0]:.0f}, {group['pct_ci'][1]:.0f}]  (rough: n = 5)")

# Comparison figure: one row per person, plus an across-people row
labels = [f"P{p} ({person[p]['n']} trials)" for p in PARTICIPANTS]
labels.append("Across 5 people\n(rough)")
rows = np.arange(len(labels))[::-1]   # first participant at the top

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True,
                         layout="constrained")
panels = [
    ("mean", "mean_ci", 0, "Mean mu change from rest (dB)"),
    ("pct", "pct_ci", 50, "Trials with lower mu (%)"),
]
for ax, (value, ci, no_change, xlabel) in zip(axes, panels):
    entries = [person[p] for p in PARTICIPANTS] + [group]
    for row, entry, is_group in zip(rows, entries,
                                    [False] * len(PARTICIPANTS) + [True]):
        lo, hi = entry[ci]
        ax.plot([lo, hi], [row, row], color="#3d3d3d", lw=2,
                solid_capstyle="round")
        ax.plot(entry[value], row, marker="D" if is_group else "o",
                ms=9 if is_group else 8, color="#3d3d3d",
                markeredgecolor="white", markeredgewidth=1.5)
    ax.axvline(no_change, color="#9a9a9a", lw=1, ls="--")
    ax.axhline(rows[-1] + 0.5, color="#d0d0d0", lw=1)   # separates group row
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", color="#ececec", lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

axes[0].set_yticks(rows, labels)
axes[0].text(0, rows[0] + 0.6, "no change", ha="center", fontsize=8,
             color="#6b6b6b")
axes[1].text(50, rows[0] + 0.6, "coin flip", ha="center", fontsize=8,
             color="#6b6b6b")
axes[1].set_xlim(0, 100)
fig.suptitle("Cz mu change during foot imagery vs rest, by participant "
             "(dots: estimate, bars: 95% bootstrap interval)")

path = OUTPUT_DIR / "m5_participant_comparison.png"
fig.savefig(path, dpi=200)
print("Saved", path)
plt.show()
