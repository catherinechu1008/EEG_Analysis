import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.integrate import trapezoid

from eeg_rehab.config import (
    PARTICIPANT, PRIMARY_CHANNEL, VOLTS_TO_UV, MU_BAND, BETA_BAND,
)
from eeg_rehab.pipeline import prepare_participant

trial_pairs, trial_table = prepare_participant(PARTICIPANT)

status = {(r["run"], r["trial"]): r["quality_status"] for r in trial_table}

sd_rows = []

for pair in trial_pairs:
    ch = pair["channels"].index(PRIMARY_CHANNEL)
    rest_sd = np.std(pair["rest"][ch]) * VOLTS_TO_UV
    foot_sd = np.std(pair["foot"][ch]) * VOLTS_TO_UV
    flagged = status[(pair["run"], pair["trial"])] == "flagged for review"
    sd_rows.append((pair["run"], pair["trial"], rest_sd, foot_sd, flagged))

    print(f"Run {pair['run']:2d} trial {pair['trial']}: "
          f"rest SD {rest_sd:5.1f} uV, imagery SD {foot_sd:5.1f} uV"
          f"{'  [flagged]' if flagged else ''}")

    
lower = 0
for run, trial, rest_sd, foot_sd, flagged in sd_rows:
    if foot_sd < rest_sd:
        lower += 1

print(f"\nImagery SD lower than rest SD in {lower}/{len(sd_rows)} trials")


fig, ax = plt.subplots(figsize=(5, 5))
for run, trial, rest_sd, foot_sd, flagged in sd_rows:
    color = "tab:red" if flagged else "tab:gray"
    ax.plot([0, 1], [rest_sd, foot_sd], marker="o", color=color, alpha=0.7)
ax.set_xticks([0, 1])
ax.set_xticklabels(["Rest\n(-2 to 0 s)", "Foot imagery\n(+1 to +3 s)"])
ax.set_xlim(-0.3, 1.3)
ax.set_ylabel("Cz standard deviation (µV)")
ax.set_title(f"Participant {PARTICIPANT}: Cz SD per trial\n(red = flagged)")
fig.tight_layout()
plt.show(block=False)

pair = trial_pairs[0]
ch = pair["channels"].index(PRIMARY_CHANNEL)
sfreq = pair["sampling_rate"]
n_samples = pair["rest"].shape[1] #pair["rest"].shape is (3,320)

freqs = np.fft.rfftfreq(n_samples, d=1 / sfreq)  #makes the list of bucket labels
print(f"\nStep 2: run {pair['run']} trial {pair['trial']}, "
      f"{n_samples} samples, bin spacing {freqs[1]:.2f} Hz, "
      f"max {freqs[-1]:.0f} Hz")

def one_sided_psd(segment_uv):
    """Single-segment PSD (periodogram) in µV²/Hz."""
    psd = np.abs(np.fft.rfft(segment_uv)) ** 2 / (sfreq * len(segment_uv))
    psd[1:-1] *= 2  # fold negative frequencies into positive ones
    return psd

rest_psd = one_sided_psd(pair["rest"][ch] * VOLTS_TO_UV)
foot_psd = one_sided_psd(pair["foot"][ch] * VOLTS_TO_UV)

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(freqs, rest_psd, label="Rest", color="tab:blue")
ax.semilogy(freqs, foot_psd, label="Foot imagery", color="tab:orange")
ax.axvspan(*MU_BAND, color="green", alpha=0.1, label="Mu 8–13 Hz")
ax.axvspan(*BETA_BAND, color="purple", alpha=0.1, label="Beta 13–30 Hz")
ax.set_xlim(0, 80)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Power spectral density (µV²/Hz)")
ax.set_title(f"Cz, run {pair['run']} trial {pair['trial']}: single-segment FFT")
ax.legend()
fig.tight_layout()
plt.show(block=False)

WELCH_SECONDS = 1.0
nperseg = int(WELCH_SECONDS * sfreq) #160 samples per piece

welch_freqs, rest_welch = welch(
    pair["rest"][ch] * VOLTS_TO_UV,
    fs=sfreq,
    nperseg=nperseg
)
_, foot_welch = welch(
    pair["foot"][ch] * VOLTS_TO_UV, fs=sfreq, nperseg=nperseg
)
print(f"\nStep 3: Welch pieces of {nperseg} samples, "
      f"bin spacing {welch_freqs[1]:.2f} Hz")

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(freqs, rest_psd, color="tab:blue", alpha=0.3, lw=1,
            label="Rest, single FFT")
ax.semilogy(freqs, foot_psd, color="tab:orange", alpha=0.3, lw=1,
            label="Imagery, single FFT")
ax.semilogy(welch_freqs, rest_welch, color="tab:blue", lw=2.5,
            label="Rest, Welch")
ax.semilogy(welch_freqs, foot_welch, color="tab:orange", lw=2.5,
            label="Imagery, Welch")
ax.axvspan(*MU_BAND, color="green", alpha=0.1)
ax.axvspan(*BETA_BAND, color="purple", alpha=0.1)
ax.set_xlim(0, 45)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Power spectral density (µV²/Hz)")
ax.set_title(f"Cz, run {pair['run']} trial {pair['trial']}: FFT vs Welch")
ax.legend()
fig.tight_layout()
plt.show(block=False)

rest_psds = []
foot_psds = []

for p in trial_pairs:
    c = p["channels"].index(PRIMARY_CHANNEL)
    _, rest_one = welch(p["rest"][c] * VOLTS_TO_UV, fs=sfreq, nperseg=nperseg)
    _, foot_one = welch(p["foot"][c] * VOLTS_TO_UV, fs=sfreq, nperseg=nperseg)
    rest_psds.append(rest_one)
    foot_psds.append(foot_one)

rest_psds = np.array(rest_psds)
foot_psds = np.array(foot_psds)

print(f"\nStep 4: PSD table shape {rest_psds.shape} (trials, frequencies)")

rest_mean = rest_psds.mean(axis=0)   # average down the rows
foot_mean = foot_psds.mean(axis=0)

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(welch_freqs, rest_mean, color="tab:blue", lw=2.5,
            label=f"Rest (mean of {len(rest_psds)} trials)")
ax.semilogy(welch_freqs, foot_mean, color="tab:orange", lw=2.5,
            label=f"Foot imagery (mean of {len(foot_psds)} trials)")
ax.axvspan(*MU_BAND, color="green", alpha=0.1, label="Mu 8–13 Hz")
ax.axvspan(*BETA_BAND, color="purple", alpha=0.1, label="Beta 13–30 Hz")
ax.set_xlim(0, 45)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Power spectral density (µV²/Hz)")
ax.set_title(f"Participant {PARTICIPANT}, Cz: average Welch PSD")
ax.legend()
fig.tight_layout()
plt.show(block=False)

def band_power(psds, band):
    in_band = (welch_freqs >= band[0]) & (welch_freqs <= band[1])
    return trapezoid(psds[:, in_band], welch_freqs[in_band], axis=1)

mu_rest = band_power(rest_psds, MU_BAND)
mu_foot = band_power(foot_psds, MU_BAND)
beta_rest = band_power(rest_psds, BETA_BAND)
beta_foot = band_power(foot_psds, BETA_BAND)

flagged = [status[(p["run"], p["trial"])] == "flagged for review"
           for p in trial_pairs]

print("\nStep 5: band power at Cz")
print(f"Mu:   imagery lower in {np.sum(mu_foot < mu_rest)}/{len(mu_rest)} trials")
print(f"Beta: imagery lower in {np.sum(beta_foot < beta_rest)}/{len(beta_rest)} trials")

fig, axes = plt.subplots(1, 2, figsize=(9, 5))
panels = [
    (axes[0], mu_rest, mu_foot, "Mu 8–13 Hz"),
    (axes[1], beta_rest, beta_foot, "Beta 13–30 Hz"),
]
for ax, rest_bp, foot_bp, title in panels:
    for r, f, flag in zip(rest_bp, foot_bp, flagged):
        color = "tab:red" if flag else "tab:gray"
        ax.plot([0, 1], [r, f], marker="o", color=color, alpha=0.7)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Rest", "Foot imagery"])
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylabel("Band power (µV²)")
    ax.set_title(title)
fig.suptitle(f"Participant {PARTICIPANT}, Cz: band power per trial (red = flagged)")
fig.tight_layout()
plt.show(block=False)

def autocovariance(x, max_lag):
    """Autocovariance of one segment for lags 0..max_lag samples."""
    x = x - x.mean()
    n = len(x)
    return np.array([np.sum(x[:n - k] * x[k:]) / n
                     for k in range(max_lag + 1)])

MAX_LAG = 40                                # 40 samples = 0.25 s
lags_ms = np.arange(MAX_LAG + 1) / sfreq * 1000

rest_acov = []
foot_acov = []
for p in trial_pairs:
    c = p["channels"].index(PRIMARY_CHANNEL)
    rest_acov.append(autocovariance(p["rest"][c] * VOLTS_TO_UV, MAX_LAG))
    foot_acov.append(autocovariance(p["foot"][c] * VOLTS_TO_UV, MAX_LAG))
rest_acov = np.array(rest_acov).mean(axis=0)
foot_acov = np.array(foot_acov).mean(axis=0)

print(f"\nStep 6: lag 0 (variance) rest {rest_acov[0]:.1f} uV^2, "
      f"imagery {foot_acov[0]:.1f} uV^2")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(lags_ms, rest_acov, color="tab:blue", lw=2, label="Rest")
ax.plot(lags_ms, foot_acov, color="tab:orange", lw=2, label="Foot imagery")
ax.axhline(0, color="black", lw=0.8)
ax.set_xlabel("Lag (ms)")
ax.set_ylabel("Autocovariance (µV²)")
ax.set_title(f"Participant {PARTICIPANT}, Cz: mean autocovariance "
             f"({len(trial_pairs)} trials, exploratory)")
ax.legend()
fig.tight_layout()
plt.show(block=False)


# Keep all figures open until closed
plt.show()