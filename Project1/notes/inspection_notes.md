# Inspection notes — Participant 1

Moved from the comment block at the end of the original `vr_rehab.py`.

## Initial example pairs (original, unprocessed data)

Participant 1, run 6:

- Rest 2.2–4.2 s: no obvious sudden spikes reported.
- Foot imagery 5.2–7.2 s: spike observed around recording time 6.45–6.70 s.
  Appears across C3, Cz, and C4.
- Flagged for review; not excluded or confirmed as an artifact.

Filtered and average-referenced copies have been created for all three runs.
The original recordings and earlier pairs remain unprocessed.
Data in `pairs` remain in volts; plots display microvolts.

## Rest-segment inspection

- Run 6: spike around 3.8 s recording time, across C3/Cz/C4.
- Run 10: spike around 12.1 s recording time, across C3/Cz/C4.
- Run 14: no equally obvious rest spike reported.
- Flagged for review; no segments excluded.

## After average referencing

Run 6: Cz voltage swings are smaller. Spikes near 3.8 s and 6.45–6.70 s are
less visible. Their cause remains uncertain; no trials excluded.

## Quality review of all extracted pairs

Recorded in `data/quality_review.csv`.

- Run 10 trial 1: possibly larger swings during foot imagery.
- Run 14 trial 8: shakier appearance during both rest and imagery.

Both flagged trials keep `include = True` on purpose: they are retained
provisionally so Milestone 5 can compare results with and without them.
Visual appearance alone cannot establish an artifact's cause.


### Step 2: single-trial FFT at Cz (run 6 trial 1)

- Bin spacing 0.5 Hz (1 / 2 s); max 80 Hz (Nyquist).
- Power drops above 40 Hz, as expected from the 1–40 Hz filter.
- Strongest power near 1 Hz; slow activity dominates, which helps
  explain why SD showed no consistent change.
- Rest and imagery lines tangled in mu and beta; one noisy trial
  is not enough to judge a difference.


  ### Step 3: Welch PSD at Cz (run 6 trial 1)

- Settings: 1 s pieces (160 samples), default 50% overlap and Hann taper;
  bin spacing 1 Hz. Same settings for rest and imagery.
- 1 s chosen as a balance: 3 pieces to average, about 6 bins inside mu.
- Welch spectrum smoother than the single FFT.
- Rest and imagery still tangled in mu and beta for this single trial.

### Step 4: average Welch PSD at Cz (24 trials)

- PSD table shape (24, 81): trials × frequencies.
- Rest and imagery averages tangled in mu and beta; no clear difference
  visible by eye.
- Possible reasons: log axis hides modest changes; foot area is deep at
  the midline; individual variation; window/reference choices.
- Settings not changed in response to this result.

### Step 5: band power per trial at Cz (24 trials)

- Band power = trapezoid area under each trial's Welch PSD (µV²).
- Mu 8–13 Hz: imagery lower in 8/24 trials (higher in 16/24).
- Beta 13–30 Hz: imagery lower in 8/24 trials (higher in 16/24).
- Most paired lines slope up; flagged trials do not stand out.
- No evidence of ERD for participant 1 at Cz. Tendency toward higher
  power during imagery, but 16/24 is not clearly beyond chance.
- Possible explanations: foot imagery can raise power at some sites;
  pre-cue anticipation in the rest window; individual variation; cue
  effects. Settings not changed in response.


### Step 6 (exploratory): autocovariance at Cz (24 trials, lags 0–40 samples)

- Lag 0 (variance): rest 369.7 µV², imagery 396.9 µV²
  (≈ 19.2 and 19.9 µV SD), consistent with Step 1.
- Smooth decline, no visible ripples: slow activity dominates;
  no clear mu-range rhythm visible.
- Rest and imagery curves very similar.
- Max lag 40 samples (250 ms) chosen to cover two 10 Hz cycles.


## Prompt for plotting Cz autocovariance

TASK: exploratory autocovariance, rest vs foot imagery, at Cz
1. For each of the 24 pairs, take the Cz row, convert to microvolts,
   subtract the segment mean, and compute the autocovariance for lags
   0–40 samples (0–250 ms), dividing by the full segment length (n).
2. Average across the 24 trials, separately for rest and imagery.
   Use identical settings for both.
3. Plot both averages on one figure: x = lag in ms, y = autocovariance
   in µV², a horizontal line at 0, legend, and a title that says
   "exploratory".
4. Sanity check: lag 0 equals the variance. Print lag 0 for each
   condition and its square root (in µV), and confirm it falls within
   the per-trial Cz SD range (I previously found 14.5–24.5 µV).
5. Plots: use plt.show(block=False) per figure and one final plt.show()
   (I run scripts from PowerShell).

WHAT I WANT EXPLAINED
- Whether the curves show repeating ripples (e.g., peaks ~75–125 ms apart
  would suggest a mu-range rhythm, 8–13 Hz) or a smooth drop.
- Whether rest and imagery differ.
- What this means in plain words, using a simple everyday analogy.

INTERPRETATION RULES
- This is exploratory; my main evidence is band power. Don't overclaim.
- A smooth drop means no rhythm is strong enough to be visible, not that
  no rhythm exists (slow activity near 1 Hz dominates this signal).
- Don't change settings to make the result look better.
- Give me a short markdown note (4–6 bullets) I can paste into
  notes/inspection_notes.md.

