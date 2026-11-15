# Power Spectrum Part 2 — Study Notes

## Day 1 — Meet the ECoG data

**Key numbers:** N = 500 samples, dt = 0.002 s, fs = 500 Hz, T = 1 s

**My answers:**
- Axes: x = time (s), y = voltage (mV)
- Samples per second: fs = 1/dt = 1/0.002 = 500 Hz. (N is also 500, but only because T = 1 s.)
- Rhythm by eye: guessed ~10 Hz. The spectrum showed 6 Hz, so counting by eye was off.

**Takeaway:**

## Day 2 — Refresh the power spectrum

**Key result:** main peak at 6 Hz, second peak at 12 Hz (a harmonic: 2 × 6)

**Key ideas:**
- A signal can be built from sine waves; the spectrum shows how much of each frequency is in it.
- df = 1/T (longer recording → finer spacing); fNQ = fs/2 (depends only on sampling rate).
- The spectrum loses timing: it can't say *when* a rhythm happened.
- Subtracting the mean only changes the 0 Hz point. Without it, that bar can be huge and squash the plot.

**My answers:**
- A spectral peak means: the signal contains a rhythm at that frequency; the taller the peak, the stronger the rhythm.
- Linear plot: to see which frequency has the most power. dB plot: to see all frequencies present, including weak ones.

**Still unclear / questions:**

**Takeaway:**

## Day 4 — Zero padding

**Key result:** 10.5 Hz sine, 1 s of data, padded to 1000 / 2000 / 10000 points. The dots for A (no zeros) and B (+1000) sit on C's curve (+9000), so all three show the same spectrum. Only B and C have a point at 10.5 Hz.

**Key ideas:**
- Zero padding = add zeros to the end before the FFT (`np.fft.fft(x, n=n_fft)`). The FFT thinks the signal is longer, so the bins get closer together: spacing = 1 / (padded length).
- The frequency range stays 0 to Nyquist. There are just more points in it (denser, not longer).
- Benefit: a point can land on the top of a peak, so its true location and height are easier to read off (A missed 10.5 Hz, so the peak looked shorter).
- The peak's width doesn't change. Only more *real* data narrows it (Day 5).

**My answers:**
- Zero padding doesn't add new information; it only makes the spectrum denser/smoother. The peak width stays the same because the added zeros aren't real data.

**Still unclear / questions:**

**Takeaway:** Zero padding is like zooming into a photo: more pixels, no new detail.

<!-- Copy this block for each new day:

## Day N — Title

**Key result:**

**Key ideas:**
-

**My answers:**
-

**Still unclear / questions:**

**Takeaway:**

-->
