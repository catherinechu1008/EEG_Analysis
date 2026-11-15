import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.signal.windows import dpss
from scipy.stats import chi2

data = loadmat("data/04_ECoG-1.mat")
print(data.keys())                 # see which variables the file holds

ecog = data["ECoG"].reshape(-1)    # voltage, flattened to 1-D
t = data["t"].reshape(-1)          # time in seconds

dt = t[1] - t[0]
fs = 1 / dt
N = len(ecog)
T = N * dt

print(f"N = {N} samples, dt = {dt} s, fs = {fs:.0f} Hz, T = {T:.2f} s")

plt.figure(figsize=(10, 3))
plt.plot(t, ecog)
plt.xlabel("Time [s]")
plt.ylabel("Voltage [mV]")
plt.title("ECoG-1 raw voltage")
plt.tight_layout()

# ---------- Day 2: power spectrum ----------
x = ecog - ecog.mean()                    # remove the mean so 0 Hz doesn't dominate
xf = np.fft.fft(x)                        # Fourier transform
Sxx = 2 * dt**2 / T * (xf * xf.conj()).real   # power, in mV^2/Hz
Sxx = Sxx[:N // 2]                        # keep frequencies from 0 up to Nyquist

df = 1 / T
fNQ = fs / 2
faxis = np.arange(0, fNQ, df)

fig, axs = plt.subplots(1, 2, figsize=(11, 3.5))
axs[0].plot(faxis, Sxx)
axs[0].set(xlabel="Frequency [Hz]", ylabel="Power [mV$^2$/Hz]", title="Linear")
axs[1].plot(faxis, 10 * np.log10(Sxx))
axs[1].set(xlabel="Frequency [Hz]", ylabel="Power [dB]", title="Decibels")
for ax in axs:
    ax.set_xlim(0, 100)                   # zoom in on low frequencies
plt.tight_layout()

print("Peak frequency:", faxis[np.argmax(Sxx)], "Hz")

                              # keep all figure windows open until closed

# ---------- Day 3: rectangular window and leakage ----------
def spectrum(x, dt):
    """Power spectrum with a rectangular window (no taper), same formula as Day 2."""
    N = len(x)
    T = N * dt
    x = x - x.mean()
    xf = np.fft.fft(x)
    Sxx = 2 * dt**2 / T * (xf * xf.conj()).real
    Sxx = Sxx[:N // 2]
    faxis = np.arange(N // 2) / T          # bins spaced 1/T apart
    return faxis, Sxx

dt_sim = 1 / 1000                          # simulated signal sampled at 1000 Hz
t_sim = np.arange(0, 1.0, dt_sim)          # exactly 1 s → bins at 0, 1, 2, ... Hz

x_on  = np.sin(2 * np.pi * 10.0 * t_sim)   # 10 whole cycles
x_off = np.sin(2 * np.pi * 10.5 * t_sim)   # 10.5 cycles → jump at the seam

f_sim, S_on  = spectrum(x_on, dt_sim)
f_sim, S_off = spectrum(x_off, dt_sim)

plt.figure(figsize=(7, 3.5))
plt.plot(f_sim, S_on,  "o-", label="10 Hz (on a bin)")
plt.plot(f_sim, S_off, "o-", label="10.5 Hz (between bins)")
plt.xlim(5, 16)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Power")
plt.title("Leakage with a rectangular window")
plt.legend()
plt.tight_layout()

plt.figure(figsize=(7, 3.5))
plt.plot(f_sim, 10 * np.log10(S_on),  "o-", label="10 Hz (on a bin)")
plt.plot(f_sim, 10 * np.log10(S_off), "o-", label="10.5 Hz (between bins)")
plt.xlim(0, 30)
plt.ylim(-60, 5)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Power [dB]")
plt.title("Leakage in decibels")
plt.legend()
plt.tight_layout()

# ---------- Day 4: zero padding ----------
def spectrum_padded(x, dt, n_fft):
    """Rectangular-window spectrum, with zeros added until the FFT length is n_fft."""
    N = len(x)
    T = N * dt                             # real recording length (zeros don't count)
    x = x - x.mean()
    xf = np.fft.fft(x, n=n_fft)            # n > N → numpy appends zeros
    Sxx = 2 * dt**2 / T * (xf * xf.conj()).real
    Sxx = Sxx[:n_fft // 2]
    faxis = np.arange(n_fft // 2) / (n_fft * dt)   # bins spaced 1/(padded length)
    return faxis, Sxx

# Same 10.5 Hz sine from Day 3 (1000 samples = 1 s of real data)
f_A, S_A = spectrum_padded(x_off, dt_sim, 1000)    # A: no zeros       → 1 Hz bins
f_B, S_B = spectrum_padded(x_off, dt_sim, 2000)    # B: +1000 zeros    → 0.5 Hz bins
f_C, S_C = spectrum_padded(x_off, dt_sim, 10000)   # C: +9000 zeros    → 0.1 Hz bins

plt.figure(figsize=(7, 3.5))
plt.plot(f_C, S_C, "-", label="C: +9000 zeros")    # line: many points
plt.plot(f_B, S_B, "s", label="B: +1000 zeros")    # squares
plt.plot(f_A, S_A, "o", label="A: no zeros")       # circles
plt.xlim(5, 16)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Power")
plt.title("10.5 Hz sine, 1 s of data, three amounts of zero padding")
plt.legend()
plt.tight_layout()

# ---------- Day 5: distinguishing nearby frequencies ----------
t_short = np.arange(1000) * dt_sim         # 1000 samples = 1 s of real data
t_long  = np.arange(4000) * dt_sim         # 4000 samples = 4 s of real data

# Same two rhythms in both: 10 Hz + 10.5 Hz (only 0.5 Hz apart)
x_short = np.sin(2 * np.pi * 10.0 * t_short) + np.sin(2 * np.pi * 10.5 * t_short)
x_long  = np.sin(2 * np.pi * 10.0 * t_long)  + np.sin(2 * np.pi * 10.5 * t_long)

# Both padded to the same FFT length → same 0.1 Hz bin spacing
f_short, S_short = spectrum_padded(x_short, dt_sim, 10000)   # 1 s + 9000 zeros
f_long,  S_long  = spectrum_padded(x_long,  dt_sim, 10000)   # 4 s + 6000 zeros

fig, axs = plt.subplots(1, 2, figsize=(11, 3.5))
axs[0].plot(f_short, S_short)
axs[0].set(xlabel="Frequency [Hz]", ylabel="Power", title="1 s of data, padded to 10000")
axs[1].plot(f_long, S_long)
axs[1].set(xlabel="Frequency [Hz]", ylabel="Power", title="4 s of data, padded to 10000")
axs[0].axvline(10.0, color="gray", linestyle="--")   # dashed lines = true frequencies
axs[0].axvline(10.5, color="gray", linestyle="--")
axs[1].axvline(10.0, color="gray", linestyle="--")
axs[1].axvline(10.5, color="gray", linestyle="--")
axs[0].set_xlim(8, 13)
axs[1].set_xlim(8, 13)
plt.tight_layout()

# ---------- Day 6: Hann taper in the time domain ----------
hann_sim = np.hanning(len(x_off))          # one weight per sample: 0 → 1 → 0
x_tapered_sim = hann_sim * x_off           # multiply sample by sample

fig, axs = plt.subplots(3, 1, figsize=(8, 7))
axs[0].plot(t_sim, hann_sim)
axs[0].set(ylabel="Weight", title="1. Hann taper")
axs[1].plot(t_sim, x_off)
axs[1].set(ylabel="Signal", title="2. Original 10.5 Hz sine")
axs[2].plot(t_sim, x_tapered_sim)
axs[2].set(xlabel="Time [s]", ylabel="Signal", title="3. Taper × sine")
plt.tight_layout()

print("First and last Hann weights:", hann_sim[0], hann_sim[-1])
print("Middle Hann weight:", hann_sim[len(hann_sim) // 2])

# ---------- Day 7: rectangular vs Hann on the ECoG ----------
# Rectangular spectrum = Sxx from Day 2 (no taper). Reuse it as-is.

hann = np.hanning(N)                      # one weight per ECoG sample
x_hann = hann * x                         # taper the mean-removed ECoG from Day 2
xf_hann = np.fft.fft(x_hann)
Sxx_hann = 2 * dt**2 / T * (xf_hann * xf_hann.conj()).real
Sxx_hann = Sxx_hann[:N // 2]

fig, axs = plt.subplots(1, 2, figsize=(11, 3.5))
axs[0].plot(faxis, 10 * np.log10(Sxx), label="Rectangular")
axs[0].plot(faxis, 10 * np.log10(Sxx_hann), label="Hann")
axs[0].set(xlabel="Frequency [Hz]", ylabel="Power [dB]", title="Full range")
axs[1].plot(faxis, 10 * np.log10(Sxx), "o-", label="Rectangular")
axs[1].plot(faxis, 10 * np.log10(Sxx_hann), "o-", label="Hann")
axs[1].set(xlabel="Frequency [Hz]", ylabel="Power [dB]", title="Zoom: 0-30 Hz")
axs[1].set_xlim(0, 30)
axs[0].set_ylim(-60, 25)                  # hide the 0 Hz point (about -300 dB after mean removal)
axs[1].set_ylim(-60, 25)
axs[0].legend()
plt.tight_layout()

# ---------- Day 8: multitaper intuition ----------
tapers = dpss(N, 2, 3)                    # 3 Slepian tapers, each one weight per ECoG sample
taper1 = tapers[0]
taper2 = tapers[1]
taper3 = tapers[2]

x_taper1 = taper1 * x                     # taper the mean-removed ECoG from Day 2
x_taper2 = taper2 * x
x_taper3 = taper3 * x

plt.figure(figsize=(8, 3))
plt.plot(t, taper1, label="Taper 1")
plt.plot(t, taper2, label="Taper 2")
plt.plot(t, taper3, label="Taper 3")
plt.axhline(0, color="gray", lw=0.5)
plt.xlabel("Time [s]")
plt.ylabel("Weight")
plt.title("Three Slepian tapers")
plt.legend()
plt.tight_layout()

fig, axs = plt.subplots(4, 1, figsize=(8, 8), sharex=True)
axs[0].plot(t, x)
axs[0].set(ylabel="Signal", title="Original ECoG (mean removed)")
axs[1].plot(t, x_taper1)
axs[1].set(ylabel="Signal", title="ECoG × taper 1")
axs[2].plot(t, x_taper2)
axs[2].set(ylabel="Signal", title="ECoG × taper 2")
axs[3].plot(t, x_taper3)
axs[3].set(xlabel="Time [s]", ylabel="Signal", title="ECoG × taper 3")
plt.tight_layout()

print("Largest weight in taper 1:", taper1.max())

# ---------- Day 9: multitaper parameters ----------
def multitaper(x, dt, NW):
    """Multitaper spectrum: NW = knob setting, uses 2*NW - 1 Slepian tapers."""
    N = len(x)
    tapers = dpss(N, NW, 2 * NW - 1)          # a stack of tapers, one per row
    x_tapered = tapers * x                    # x times each taper (one row each)
    xf = np.fft.fft(x_tapered, axis=1)        # FFT of each row
    S = 2 * dt * (xf * xf.conj()).real        # one power spectrum per taper (tapers already scaled)
    S = S[:, :N // 2]                         # keep 0 Hz up to Nyquist
    return S.mean(axis=0)                     # average the power spectra

S_mt1 = multitaper(x, dt, 1)                  # 1 taper
S_mt2 = multitaper(x, dt, 2)                  # 3 tapers (Day 8 setting)
S_mt4 = multitaper(x, dt, 4)                  # 7 tapers

plt.figure(figsize=(8, 4))
plt.plot(faxis, 10 * np.log10(S_mt1), "o-", label="Setting 1 (1 taper)")
plt.plot(faxis, 10 * np.log10(S_mt2), "o-", label="Setting 2 (3 tapers)")
plt.plot(faxis, 10 * np.log10(S_mt4), "o-", label="Setting 4 (7 tapers)")
plt.xlim(0, 30)
plt.ylim(-40, 25)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Power [dB]")
plt.title("ECoG multitaper spectrum, three knob settings")
plt.legend()
plt.tight_layout()

# ---------- Day 10: confidence intervals ----------
plt.close("all")                              # hide earlier days' figures; delete this line to see them again
K2 = 3                                        # setting 2 uses 3 tapers
lower2 = 2 * K2 * S_mt2 / chi2.ppf(0.975, 2 * K2)   # two-sided 95%: 0.975 gives the LOWER bound
upper2 = 2 * K2 * S_mt2 / chi2.ppf(0.025, 2 * K2)   # 0.025 gives the UPPER bound

K4 = 7                                        # setting 4 uses 7 tapers
lower4 = 2 * K4 * S_mt4 / chi2.ppf(0.975, 2 * K4)
upper4 = 2 * K4 * S_mt4 / chi2.ppf(0.025, 2 * K4)

fig, axs = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
axs[0].fill_between(faxis, 10 * np.log10(lower2), 10 * np.log10(upper2), alpha=0.3, label="95% interval")
axs[0].plot(faxis, 10 * np.log10(S_mt2), "o-", label="Estimate")
axs[0].set(xlabel="Frequency [Hz]", ylabel="Power [dB]", title="Setting 2 (3 tapers)")
axs[1].fill_between(faxis, 10 * np.log10(lower4), 10 * np.log10(upper4), alpha=0.3)
axs[1].plot(faxis, 10 * np.log10(S_mt4), "o-")
axs[1].set(xlabel="Frequency [Hz]", title="Setting 4 (7 tapers)")
axs[0].set_xlim(0, 30)
axs[1].set_xlim(0, 30)
axs[0].set_ylim(-40, 25)
axs[0].legend()
plt.tight_layout()


plt.show()
