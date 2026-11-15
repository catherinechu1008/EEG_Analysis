import sys
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eeg_rehab.config import (
    PARTICIPANT, CHANNELS, PRIMARY_CHANNEL, REST_LABEL, FOOT_LABEL,
    VOLTS_TO_UV, REST_WINDOW, IMAGERY_WINDOW, EPOCH_WINDOW,
)
from eeg_rehab.data import load_runs
from eeg_rehab.trials import get_task_annotations, window_has_condition
from eeg_rehab.preprocessing import preprocess_runs
from eeg_rehab.config import (
    PARTICIPANT, CHANNELS, PRIMARY_CHANNEL, REST_LABEL, FOOT_LABEL,
    VOLTS_TO_UV, REST_WINDOW, IMAGERY_WINDOW, EPOCH_WINDOW, MU_BAND,
)

recordings = load_runs(PARTICIPANT)
_, referenced_runs = preprocess_runs(recordings)

epochs = []
epoch_keys = []

for run_number, recording in referenced_runs.items():
    sfreq = recording.info["sfreq"]
    n_samples = round((EPOCH_WINDOW[1] - EPOCH_WINDOW[0]) * sfreq)
    annotations = get_task_annotations(recording)
    foot_cues = [onset for onset, end, label in annotations
                 if label == FOOT_LABEL]

    for trial_number, cue in enumerate(foot_cues, start=1):
        start_sample = round((cue + EPOCH_WINDOW[0]) * sfreq)
        start = start_sample / sfreq
        stop = (start_sample + n_samples) / sfreq

        # Before the cue must be all rest, after the cue all foot imagery
        rest_ok = window_has_condition(start, cue, REST_LABEL, annotations)
        foot_ok = window_has_condition(cue, stop, FOOT_LABEL, annotations)
        if not (rest_ok and foot_ok):
            print(f"Skipped run {run_number} trial {trial_number}")
            continue

        epoch = recording.get_data(picks=CHANNELS, start=start_sample,
                                   stop=start_sample + n_samples)
        epochs.append(epoch)
        epoch_keys.append((run_number, trial_number))

epochs = np.array(epochs)
print(f"\nStep 1b: epochs shape {epochs.shape} (trials, channels, samples)")
print(f"First: run {epoch_keys[0][0]} trial {epoch_keys[0][1]}, "
      f"last: run {epoch_keys[-1][0]} trial {epoch_keys[-1][1]}")


times = np.arange(epochs.shape[2]) / sfreq + EPOCH_WINDOW[0]
print(f"Time axis: {times[0]:.3f} to {times[-1]:.3f} s relative to cue")

ch = CHANNELS.index(PRIMARY_CHANNEL)
run, trial = epoch_keys[0]

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(times, epochs[0, ch] * VOLTS_TO_UV, color="black", lw=1)
ax.axvline(0, color="red", lw=1.5, label="Cue (time 0)")
ax.axvspan(*REST_WINDOW, color="tab:blue", alpha=0.15, label="Rest window")
ax.axvspan(*IMAGERY_WINDOW, color="tab:orange", alpha=0.15,
           label="Imagery window")
ax.set_xlim(times[0], times[-1])
ax.set_xlabel("Time relative to cue (s)")
ax.set_ylabel("Cz (µV)")
ax.set_title(f"Participant {PARTICIPANT}, run {run} trial {trial}: "
             f"cue-aligned epoch")
ax.legend(loc="upper right")
fig.tight_layout()
plt.show(block=False)

from scipy.signal import spectrogram

WINDOW_SECONDS = 1.0
STEP_SECONDS = 0.1

nperseg = round(WINDOW_SECONDS * sfreq)
noverlap = nperseg - round(STEP_SECONDS * sfreq)

trial_uv = epochs[0, ch] * VOLTS_TO_UV
tf_freqs, tf_times, tf_power = spectrogram(
    trial_uv, fs=sfreq, window="hann", nperseg=nperseg,
    noverlap=noverlap, scaling="density", mode="psd",
)
tf_times = tf_times + EPOCH_WINDOW[0]   # window centres relative to cue

print(f"\nStep 2: power map shape {tf_power.shape} (frequencies, times)")
print(f"Frequency spacing {tf_freqs[1] - tf_freqs[0]:.1f} Hz, "
      f"time step {tf_times[1] - tf_times[0]:.2f} s")
print(f"Window centres from {tf_times[0]:.2f} to {tf_times[-1]:.2f} s")

shown = (tf_freqs >= 1) & (tf_freqs <= 40)
power_db = 10 * np.log10(tf_power[shown])   # dB relative to 1 µV²/Hz

fig, ax = plt.subplots(figsize=(9, 4))
mesh = ax.pcolormesh(tf_times, tf_freqs[shown], power_db,
                     shading="nearest", cmap="viridis")
ax.axvline(0, color="red", lw=1.5, label="Cue (time 0)")
for f in (8, 13, 30):
    ax.axhline(f, color="white", lw=0.8, ls="--")
ax.set_xlim(times[0], times[-1])
ax.set_xlabel("Time relative to cue (s), window centre")
ax.set_ylabel("Frequency (Hz)")
ax.set_title(f"Participant {PARTICIPANT}, run {run} trial {trial}: "
             f"Cz spectrogram (1 s window, raw power)")
fig.colorbar(mesh, ax=ax, label="Power (dB re 1 µV²/Hz)")
ax.legend(loc="upper right")
fig.tight_layout()
plt.show(block=False)

BASELINE_CENTRES = (-1.5, -0.5) 

centres = np.round(tf_times, 6)
in_baseline = ((centres >= BASELINE_CENTRES[0])
               & (centres <= BASELINE_CENTRES[1]))

# One rest level per frequency: average across the baseline columns
baseline = tf_power[:, in_baseline].mean(axis=1, keepdims=True)
change_db = 10 * np.log10(tf_power / baseline)

print(f"\nStep 3: {in_baseline.sum()} baseline columns, centres "
      f"{centres[in_baseline][0]:.1f} to {centres[in_baseline][-1]:.1f} s")
print(f"Change map shape {change_db.shape} (frequencies, times)")

fig, ax = plt.subplots(figsize=(9, 4))
mesh = ax.pcolormesh(tf_times, tf_freqs[shown], change_db[shown],
                     shading="nearest", cmap="RdBu_r", vmin=-10, vmax=10)
ax.axvline(0, color="black", lw=1.5, label="Cue (time 0)")
for t in BASELINE_CENTRES:
    ax.axvline(t, color="grey", lw=1, ls=":")
for f in (8, 13, 30):
    ax.axhline(f, color="black", lw=0.8, ls="--")
ax.set_xlim(times[0], times[-1])
ax.set_xlabel("Time relative to cue (s), window centre")
ax.set_ylabel("Frequency (Hz)")
ax.set_title(f"Participant {PARTICIPANT}, run {run} trial {trial}: "
             f"Cz change from rest (single trial)")
fig.colorbar(mesh, ax=ax, label="Change from rest (dB)")
ax.legend(loc="upper right")
fig.tight_layout()
plt.show(block=False)

# --- Step 4: change-from-rest map for every trial, then average ---
# Each trial is compared with its OWN rest level before averaging
all_change_db = []
for epoch in epochs:
    _, _, power = spectrogram(
        epoch[ch] * VOLTS_TO_UV, fs=sfreq, window="hann", nperseg=nperseg,
        noverlap=noverlap, scaling="density", mode="psd",
    )
    trial_baseline = power[:, in_baseline].mean(axis=1, keepdims=True)
    all_change_db.append(10 * np.log10(power / trial_baseline))

all_change_db = np.array(all_change_db)       # (trials, frequencies, times)
mean_change_db = all_change_db.mean(axis=0)   # (frequencies, times)

print(f"\nStep 4: {all_change_db.shape[0]} trial maps, "
      f"each {all_change_db.shape[1:]} (frequencies, times)")

# One number per trial: average mu change during the imagery window
# Centres 1.5 to 2.5 s cover only 1 to 3 s, the Milestone 3 imagery window
IMAGERY_CENTRES = (1.5, 2.5)
in_imagery = ((centres >= IMAGERY_CENTRES[0])
              & (centres <= IMAGERY_CENTRES[1]))
in_mu = (tf_freqs >= MU_BAND[0]) & (tf_freqs <= MU_BAND[1])
mu_change = all_change_db[:, in_mu][:, :, in_imagery].mean(axis=(1, 2))
print(f"Mu change in imagery window: lower than rest in "
      f"{(mu_change < 0).sum()}/{len(mu_change)} trials, "
      f"average {mu_change.mean():.2f} dB")

fig, ax = plt.subplots(figsize=(9, 4))
mesh = ax.pcolormesh(tf_times, tf_freqs[shown], mean_change_db[shown],
                     shading="nearest", cmap="RdBu_r", vmin=-3, vmax=3)
ax.axvline(0, color="black", lw=1.5, label="Cue (time 0)")
for t in BASELINE_CENTRES:
    ax.axvline(t, color="grey", lw=1, ls=":")
for t in IMAGERY_CENTRES:
    ax.axvline(t, color="tab:orange", lw=1, ls=":")
for f in (8, 13, 30):
    ax.axhline(f, color="black", lw=0.8, ls="--")
ax.set_xlim(times[0], times[-1])
ax.set_xlabel("Time relative to cue (s), window centre")
ax.set_ylabel("Frequency (Hz)")
ax.set_title(f"Participant {PARTICIPANT}: Cz change from rest, "
             f"average of {all_change_db.shape[0]} trials")
fig.colorbar(mesh, ax=ax, label="Change from rest (dB)")
ax.legend(loc="upper right")
fig.tight_layout()
plt.show(block=False)

# --- Step 5: check — mu change two ways on the same trials ---
import csv
from eeg_rehab.config import TRIAL_TABLE_CSV

# Are these the same trials Milestone 3 used?
with open(TRIAL_TABLE_CSV, newline="") as f:
    m3_keys = [(int(row["run"]), int(row["trial"]))
               for row in csv.DictReader(f)
               if row["extraction_status"] == "extracted"]
print(f"\nStep 5: same trials as Milestone 3? {m3_keys == epoch_keys}")

raw_way = []
db_way = []
for epoch in epochs:
    _, _, power = spectrogram(
        epoch[ch] * VOLTS_TO_UV, fs=sfreq, window="hann", nperseg=nperseg,
        noverlap=noverlap, scaling="density", mode="psd",
    )
    mu_power = power[in_mu]                   # (mu frequencies, times)
    rest_mu = mu_power[:, in_baseline]
    imagery_mu = mu_power[:, in_imagery]

    # Way 1: average raw power first, then compare with rest once
    raw_way.append(10 * np.log10(imagery_mu.mean() / rest_mu.mean()))

    # Way 2: compare each spot with rest in dB first, then average
    rest_level = rest_mu.mean(axis=1, keepdims=True)
    db_way.append((10 * np.log10(imagery_mu / rest_level)).mean())

raw_way = np.array(raw_way)
db_way = np.array(db_way)
print(f"Way 2 matches Step 4? {np.allclose(db_way, mu_change)}")
print(f"Way 1 (raw first): lower in {(raw_way < 0).sum()}/{len(raw_way)}, "
      f"average {raw_way.mean():.2f} dB")
print(f"Way 2 (dB first):  lower in {(db_way < 0).sum()}/{len(db_way)}, "
      f"average {db_way.mean():.2f} dB")

print("\nrun trial  raw-first  dB-first")
for (r, t), a, b in zip(epoch_keys, raw_way, db_way):
    flip = "  <- disagree" if (a < 0) != (b < 0) else ""
    print(f"{r:>3} {t:>5}  {a:>8.2f}  {b:>8.2f}{flip}")


# --- Step 6: average map without the downward tilt ---
# Divide by rest for each trial, average the ratios across trials,
# and convert to dB only once at the end
all_ratio = []
for epoch in epochs:
    _, _, power = spectrogram(
        epoch[ch] * VOLTS_TO_UV, fs=sfreq, window="hann", nperseg=nperseg,
        noverlap=noverlap, scaling="density", mode="psd",
    )
    trial_baseline = power[:, in_baseline].mean(axis=1, keepdims=True)
    all_ratio.append(power / trial_baseline)

mean_ratio_db = 10 * np.log10(np.array(all_ratio).mean(axis=0))

rest_check = mean_ratio_db[in_mu][:, in_baseline].mean()
imagery_mu = mean_ratio_db[in_mu][:, in_imagery].mean()
print(f"\nStep 6: mu during rest vs itself {rest_check:.2f} dB "
      f"(should be close to 0)")
print(f"Mu during imagery vs rest {imagery_mu:.2f} dB")

fig, ax = plt.subplots(figsize=(9, 4))
mesh = ax.pcolormesh(tf_times, tf_freqs[shown], mean_ratio_db[shown],
                     shading="nearest", cmap="RdBu_r", vmin=-3, vmax=3)
ax.axvline(0, color="black", lw=1.5, label="Cue (time 0)")
for t in BASELINE_CENTRES:
    ax.axvline(t, color="grey", lw=1, ls=":")
for t in IMAGERY_CENTRES:
    ax.axvline(t, color="tab:orange", lw=1, ls=":")
for f in (8, 13, 30):
    ax.axhline(f, color="black", lw=0.8, ls="--")
ax.set_xlim(times[0], times[-1])
ax.set_xlabel("Time relative to cue (s), window centre")
ax.set_ylabel("Frequency (Hz)")
ax.set_title(f"Participant {PARTICIPANT}: Cz change from rest, "
             f"average of {len(all_ratio)} trials (ratios averaged first)")
fig.colorbar(mesh, ax=ax, label="Change from rest (dB)")
ax.legend(loc="upper right")
fig.tight_layout()
plt.show(block=False)

# --- Step 7: single-trial examples next to the average ---
# Trials chosen by rule, not by how their maps look: lowest, middle and
# highest raw-first mu change (Step 5), plus the two flagged trials
order = np.argsort(raw_way)
picks = [
    ("Lowest mu", order[0]),
    ("Middle mu", order[len(order) // 2]),
    ("Highest mu", order[-1]),
    ("Flagged", epoch_keys.index((10, 1))),
    ("Flagged", epoch_keys.index((14, 8))),
]
ratio_maps = np.array(all_ratio)   # (trials, frequencies, times)

fig, axes = plt.subplots(2, 3, figsize=(14, 7), sharex=True, sharey=True,
                         layout="constrained")
for ax, (label, i) in zip(axes.flat, picks):
    r, t = epoch_keys[i]
    single_db = 10 * np.log10(ratio_maps[i][shown])
    mesh = ax.pcolormesh(tf_times, tf_freqs[shown], single_db,
                         shading="nearest", cmap="RdBu_r", vmin=-10, vmax=10)
    ax.set_title(f"{label}: run {r} trial {t}\n"
                 f"mu change {raw_way[i]:+.2f} dB")
    fig.colorbar(mesh, ax=ax, label="dB (±10)")

ax_avg = axes.flat[-1]
mesh = ax_avg.pcolormesh(tf_times, tf_freqs[shown], mean_ratio_db[shown],
                         shading="nearest", cmap="RdBu_r", vmin=-3, vmax=3)
ax_avg.set_title(f"Average of {len(ratio_maps)} trials\n"
                 f"(narrower colour scale)")
fig.colorbar(mesh, ax=ax_avg, label="dB (±3)")

for ax in axes.flat:
    ax.axvline(0, color="black", lw=1.2)
    for t in BASELINE_CENTRES:
        ax.axvline(t, color="grey", lw=1, ls=":")
    for t in IMAGERY_CENTRES:
        ax.axvline(t, color="tab:orange", lw=1, ls=":")
    for f in (8, 13, 30):
        ax.axhline(f, color="black", lw=0.6, ls="--")
    ax.set_xlim(times[0], times[-1])
for ax in axes[1]:
    ax.set_xlabel("Time relative to cue (s)")
for ax in axes[:, 0]:
    ax.set_ylabel("Frequency (Hz)")
fig.suptitle(f"Participant {PARTICIPANT}, Cz: single trials vs average "
             f"(change from rest)")
plt.show(block=False)

# --- Step 8 (exploratory): window length trade-off, 1 s vs 0.5 s ---
def average_change(window_seconds):
    """Ratio-averaged change map and per-trial raw-first mu change."""
    n_win = round(window_seconds * sfreq)
    n_overlap = n_win - round(STEP_SECONDS * sfreq)
    half = window_seconds / 2
    ratios, mu_raw = [], []
    for epoch in epochs:
        freqs_w, times_w, power = spectrogram(
            epoch[ch] * VOLTS_TO_UV, fs=sfreq, window="hann", nperseg=n_win,
            noverlap=n_overlap, scaling="density", mode="psd",
        )
        times_w = np.round(times_w + EPOCH_WINDOW[0], 6)
        # Keep slices whose whole window lies inside rest or imagery
        base = ((times_w - half >= REST_WINDOW[0])
                & (times_w + half <= REST_WINDOW[1]))
        task = ((times_w - half >= IMAGERY_WINDOW[0])
                & (times_w + half <= IMAGERY_WINDOW[1]))
        mu = (freqs_w >= MU_BAND[0]) & (freqs_w <= MU_BAND[1])

        rest_level = power[:, base].mean(axis=1, keepdims=True)
        ratios.append(power / rest_level)
        mu_raw.append(10 * np.log10(power[mu][:, task].mean()
                                    / power[mu][:, base].mean()))
    mean_db = 10 * np.log10(np.array(ratios).mean(axis=0))
    return freqs_w, times_w, mean_db, np.array(mu_raw), base.sum(), mu.sum()

windows = {w: average_change(w) for w in (1.0, 0.5)}

for w, (f_w, t_w, m_db, mu_raw, n_base, n_mu) in windows.items():
    print(f"\nStep 8, {w} s window: {f_w[1] - f_w[0]:.0f} Hz rows, "
          f"{n_mu} rows in mu, {n_base} baseline slices, "
          f"centres {t_w[0]:.2f} to {t_w[-1]:.2f} s")
    print(f"  Mu lower than rest in {(mu_raw < 0).sum()}/{len(mu_raw)} "
          f"trials (raw-first)")

fig, axes = plt.subplots(1, 2, figsize=(14, 4.5), sharey=True,
                         layout="constrained")
for ax, (w, (f_w, t_w, m_db, *_)) in zip(axes, windows.items()):
    keep = (f_w >= 1) & (f_w <= 40)
    mesh = ax.pcolormesh(t_w, f_w[keep], m_db[keep], shading="nearest",
                         cmap="RdBu_r", vmin=-3, vmax=3)
    ax.axvline(0, color="black", lw=1.5)
    for f in (8, 13, 30):
        ax.axhline(f, color="black", lw=0.8, ls="--")
    ax.set_xlim(times[0], times[-1])
    ax.set_xlabel("Time relative to cue (s), window centre")
    ax.set_title(f"{w} s window: {f_w[1] - f_w[0]:.0f} Hz rows, "
                 f"each slice mixes {w} s")
axes[0].set_ylabel("Frequency (Hz)")
fig.colorbar(mesh, ax=axes, label="Change from rest (dB)")
fig.suptitle(f"Participant {PARTICIPANT}, Cz: window length trade-off "
             f"(exploratory, average of {len(epochs)} trials)")
plt.show(block=False)



# Keep all figures open until closed
plt.show()