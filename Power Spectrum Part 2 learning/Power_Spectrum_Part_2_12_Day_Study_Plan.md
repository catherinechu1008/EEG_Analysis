# Power Spectrum Part 2 — 12-Day Study Plan

**Pace:** About 30 minutes per day (6 hours total)
**Goal:** Build practical spectral-analysis skills for EEG, computational neuroscience, and your motor-imagery / VR rehabilitation portfolio.
**Source:** [The Power Spectrum (Part 2), Case Studies in Neural Data Analysis](https://mark-kramer.github.io/Case-Studies-Python/04.html)
**Progress:** 10 of 12 days completed.

## Daily routine

- 5 minutes: review the previous session.
- 10 minutes: learn the day's concept.
- 10 minutes: complete the small coding task.
- 5 minutes: answer the understanding check in your own words.

Use one notebook throughout and reuse earlier code. Focus on understanding and application rather than memorizing derivations. If setup or debugging takes the session, continue the same day next time.

## Daily plan

### Day 1 — Meet the ECoG data
- [x] Completed
**Learn:** Sampling rate, duration, and the difference between ECoG and scalp EEG.
**Code:** Load the chapter's data and plot voltage against time.
**Check:** What does each axis represent? How many samples are recorded per second?
**Notes:**

### Day 2 — Refresh the power spectrum
- [x] Completed
**Learn:** Connect the waveform to its frequency content.
**Code:** Compute and plot the spectrum; compare linear power and decibels.
**Check:** What does a spectral peak tell you?
**Notes:**

### Day 3 — Rectangular windows and leakage
- [x] Completed
**Learn:** Understand what happens when we select a short recording.
**Code:** Generate a sine wave and inspect the spectrum of a short segment. Try a frequency that does not complete an integer number of cycles in the segment.
**Check:** Why might power appear around the signal's frequency?
**Notes:**
- The FFT treats the segment as a loop that repeats forever. For 10.5 Hz, the wave doesn't finish a whole cycle, so where the end meets the start there is a jump. To build that jump, the FFT needs many frequencies, so power shows up at nearby frequencies — this is leakage.
- Frequency bins are spaced 1/T apart (1 s → 1 Hz). 10 Hz sits on a bin → one clean spike. 10.5 Hz falls between bins → leaks. With T = 2 s, 10.5 Hz sits on a bin and doesn't leak.
- Leakage makes a peak look shorter (tallest 10.5 Hz dot ≈ 40% of the 10 Hz spike), since the power is split across bins.
- In dB, rectangular-window leakage reaches every bin and falls off slowly (~6 dB per doubling of distance). A strong EEG peak or line noise can bury a weak rhythm far away.

### Day 4 — Zero padding
- [x] Completed
**Learn:** Separate a smoother-looking spectrum from additional information.
**Code:** Plot the same signal with three amounts of zero padding.
**Check:** Did you collect more data, or only change how densely the spectrum is displayed?
**Notes:**
- Zero padding adds zeros before the FFT, so the bins get closer together (spacing = 1 / padded length). The frequency range doesn't change; there are just more points in it.
- No new information: the unpadded and lightly padded points sit exactly on the heavily padded curve. It's the same spectrum, drawn in more detail.
- Useful for reading off a peak's true location and height (without padding, 10.5 Hz had no point and looked shorter).
- The peak's width stays the same. Only more real data makes it narrower.

### Day 5 — Distinguishing nearby frequencies
- [x] Completed
**Learn:** Explore the effect of recording length.
**Code:** Combine two nearby frequencies; compare adding zeros with generating a longer recording.
**Check:** Which change helps separate the peaks, and why?
**Notes:**
- Two rhythms can be told apart only if the resolution (1/T) is smaller than the gap between them. 10 and 10.5 Hz (0.5 Hz gap) need more than 2 s of data.
- 1 s padded to 10000: still one bump (top ≈ 10.2 Hz, between the true frequencies). The dots are dense, but each hump is still wide.
- 4 s padded to 10000: two clean peaks at 10.0 and 10.5 Hz.
- Zero padding shrinks the bin spacing, not the hump width. Only more real data makes humps narrower so they stop overlapping.

### Day 6 — Hann taper in the time domain
- [x] Completed
**Learn:** Understand how a taper weights samples.
**Code:** Plot the taper, original signal, and their element-by-element product.
**Check:** Which part of the recording receives the most weight?
**Notes:**
- A taper is one weight per sample; apply it by multiplying sample by sample (`hann * x`). A rectangular window weights every sample 1; a Hann taper is a smooth hill: 0 → 1 → 0.
- The middle of the recording gets the most weight (about 1) and keeps its full height; samples near the edges get almost no weight and fade to exactly 0.
- The tapered signal still wiggles at the same frequency; only its height changes. Both ends now sit at 0, so there's no jump at the seam → less leakage.
- Cost: the faded edges barely count, so the recording acts shorter than it is → broader peaks (links to Day 5). Day 7 tests this trade-off.
- Middle weight printed 0.99999… not exactly 1 because N = 1000 is even, so the peak falls between two samples.

### Day 7 — Compare rectangular and Hann spectra
- [x] Completed
**Learn:** Examine the trade-off between leakage reduction and broader peaks.
**Code:** Compare both methods on the same ECoG segment.
**Check:** What improves, and what detail might become harder to distinguish?
**Notes:**
- Every peak has two parts: a center hump and tails (leakage). They have different causes, and Hann changes them in opposite directions.
  - Center hump: set by how long the recording *acts*. Hann fades the edges → acts like ~0.5 s → hump ~2× wider (±2 Hz vs ±1 Hz). Cost.
  - Tails: set by the jump at the seam. Hann has no jump → tails far quieter (nearest bump ≈ −31 dB vs −13 dB). Gain.
- Which is "better" depends on the situation:
  - Weak rhythm far from a strong one → tails matter → Hann.
  - Two similar-size rhythms very close together → hump width matters → rectangular (and both still need T > 1/gap, Day 5).
- ECoG (T = 1 s, 1 Hz bins, peak at 6 Hz): at 7 Hz rectangular drops to −18.8 dB but Hann is still +5.9 dB (wider peak). From 8–12 Hz rectangular is flat (~−3 dB, leakage from 6 Hz); Hann shows a dip at 10 Hz (~−36 dB) and a small bump near 12 Hz that leakage had covered.
- Hann's peak is lower (17.1 → 10.7 dB) for two reasons: the taper keeps only ~38% of a steady signal's power (≈ −4 dB everywhere), and the rest is spread over more bins (≈ −2 dB).
- That 38% assumes a steady rhythm. A burst in the middle of the window keeps ≈ 100%; a burst near the edges is almost erased. Hann describes mostly the middle of the window (one motivation for multitaper, Day 8).
- To compare power between spectra (e.g. rest vs imagery, Day 11), use the same taper for both.
- Plotting: the 0 Hz point is ≈ −300 dB after mean removal, so set a y-limit or it squashes the plot.

### Day 8 — Multitaper intuition
- [x] Completed
**Learn:** Understand why we use several differently shaped tapers.
**Code:** Plot several tapers and the signals they produce.
**Check:** What gets averaged: the tapers, the signals, or their power spectra?
**Notes:**
- One Hann taper has two problems: (1) it wastes the edges (a 10 µV sample at 0.1 s becomes 1 µV, so it adds only ~1/100 of the power of a middle sample, and a burst near the start almost disappears); (2) one spectrum is noisy, too high or too low by chance.
- Multitaper: multiply the recording by several different tapers → FFT each → one power spectrum per taper → average the power spectra.
- Average the **power spectra**, not the tapers (that just makes one new taper) and not the tapered signals (+ and − values cancel). Power is never negative, so nothing cancels.
- Averaging reduces noise (estimates 30, 75, 45, 58 → 52, close to the true 50), but only if the tapers are different. Hann used 4 times gives 30, 30, 30, 30 → 30, so averaging does nothing.
- Slepian (DPSS) tapers, from `dpss(N, 2, 3)`, cover different parts of the recording: taper 1 = middle (like Hann), taper 2 = quarter points (≈0 in the middle), taper 3 = edges (0.89 at 0.1 s, where Hann is ≈0.1).
- How the shapes are chosen: taper 1 = the lowest-leakage shape; each next taper = lowest leakage while being orthogonal to the earlier ones (multiply sample by sample and add up → 0). Pattern: taper k crosses zero k − 1 times.
- Negative weights flip a sample's sign; squaring for power removes the sign, so −0.98 counts like +0.98.
- Python scales each taper so its squared weights add to 1, so the weights max out around 0.07, not 1. Only the shape matters.

### Day 9 — Multitaper parameters
- [x] Completed
**Learn:** Connect duration, bandwidth, and taper count.
**Code:** Change the time-bandwidth setting and compare the resulting spectra.
**Check:** What changes when you allow more frequency smoothing?
**Notes:**
- The `2` in `dpss(N, 2, 3)` is a knob (the time-bandwidth product, NW) that sets how wide each peak becomes. This spreading is called frequency smoothing.
- Pure 6 Hz sine, 1 s, power at each Hz (max = 100): setting 1 → only 6 Hz (5 and 7 Hz ≈ 6); setting 2 → 5, 6, 7 Hz all ≈ 100; setting 4 → 3–9 Hz all ≈ 100.
- Number of tapers = 2 × setting − 1 (1 → 1, 2 → 3, 4 → 7). That's why Day 8 used 3 tapers.
- Trade-off: knob up → more tapers to average → less noise, but wider peaks → nearby details blur. Knob down → sharper but noisier.
- ECoG, settings 1/2/4: setting 1 is jagged but shows the 12 Hz bump (1.5 dB vs −13 / −10 on either side). Setting 4 is smooth, but 6 Hz becomes a flat 3–9 Hz plateau (~8.7 dB) and the 12 Hz bump disappears. Setting 2 is in between.
- A longer recording gives narrower smoothing for the same setting (width = setting ÷ T Hz on each side), the same lesson as Day 5.
- Code: Slepian tapers are already scaled (squared weights add to 1), so the power formula is `2*dt*|fft|²` instead of `2*dt²/T*|fft|²`. Same units.
- **My answer:** More smoothing makes the spectrum less noisy, but the peaks get wider, so some details can be lost.

### Day 10 — Confidence intervals
- [x] Completed
**Learn:** Understand uncertainty around estimated power.
**Code:** Add confidence bounds using a correctly implemented two-sided interval.
**Check:** What does a wider interval tell you about the estimate?
**Implementation note:** For a two-sided 95% chi-square interval, use the 0.025 and 0.975 quantiles. The chapter's example uses 0.05 and 0.95 despite labeling its result 95%; do not copy that labeling unchanged.
**Notes:**
- Each spectrum point is a guess. A confidence interval is the range where the true power probably lies. 95% means about 95 of 100 intervals built this way contain the true value, so a value outside the range is unlikely but still possible.
- More tapers → narrower interval. For a guess of 100: 1 taper → 27 to 3950; 3 tapers → 42 to 485; 7 tapers → 54 to 249. The cost is wider peaks (Day 9), so you're more sure about a blurrier picture.
- The interval is lopsided: the true power can be much higher than the guess (×4.85) but less far below it (×0.415, 3 tapers).
- Bounds come from the chi-square distribution (`chi2.ppf`). Two-sided 95% → discard 2.5% at each end → cut-offs 0.025 and 0.975. 99% → 0.005 and 0.995. The chapter's 0.05 / 0.95 discards 10% in total, so it's really a 90% interval (48 to 367, which only looks tighter).
- Formula with K tapers: lower = 2K·S / `chi2.ppf(0.975, 2K)`, upper = 2K·S / `chi2.ppf(0.025, 2K)`. 0.975 gives the lower bound because we divide by it.
- ECoG with 3 tapers: 10 Hz range is −13.1 to −2.5 dB and 12 Hz range is −6.6 to 4.0 dB. They overlap, so we can't be sure the 12 Hz bump is higher. That means "can't tell" (needs more data or trials), not "fake". Relevant for Day 11's single rest vs imagery windows.
- **My answer:** A wider interval means I'm less certain about the true power.

### Day 11 — Apply it to your EEG project
- [ ] Completed
**Learn:** Transfer one method to familiar data.
**Code:** Using prepared, equal-length rest and imagery windows from one channel, plot their spectra with identical settings.
**Check:** Which settings must stay consistent for a fair comparison?
**Scope:** This is a practice comparison. A conclusion about motor imagery requires examining multiple trials. Preserve comparable PSD units and scaling; do not independently normalize each condition to its own maximum when comparing power.
**Notes:**

### Day 12 — Consolidate and explain
- [ ] Completed
**Learn:** Turn your work into a readable notebook.
**Code:** Select three useful figures and write a short explanation beneath each.
**Check:** Can you explain your method choice, one observation, and one limitation?
**Notes:**

## Completion goals

- Explain leakage, tapering, and the limits of zero padding.
- Describe the trade-off involved in multitaper estimation.
- Interpret uncertainty around a spectral estimate.
- Apply consistent analysis settings to rest and imagery data.
- Produce one small notebook with code, figures, and explanations.

Days 1–10 follow the chapter's topics. Days 11–12 are added application and consolidation activities. The convolution appendix is optional extra study.

