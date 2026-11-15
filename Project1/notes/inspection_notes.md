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

- Lesson: averaging dB (log) values ≠ dB of averaged power. Averaging
  logs is pulled downward by noise. Average power/ratios first, convert
  to dB at the end. Sanity check: rest vs itself should give 0 dB.

### Step 6: average map, ratios averaged before dB (24 trials, Cz)
- Per trial: divide by own rest level; average ratios; dB once at end.
- Sanity check: mu rest vs itself -0.09 dB (≈ 0, no tilt).
- Rest area paler than Step 4 map: Step 4's blue was method bias.
- Mu during imagery (centres 1.5–2.5 s): +2.07 dB; strip looks red.
  Average can be pulled up by a few large trials; trial count is the
  fairer summary: higher in 17/24 (Step 5 raw-first).
- Conclusion: no mu ERD for participant 1 at Cz; tendency toward
  higher power (ERS) during foot imagery. Not conclusive for one person.
- Decision: per-trial raw-first summary (Way 1) is the primary trial
  number; ratio-averaged map (Step 6) is the primary display.
  Step 4 dB-first map kept only as an illustration of the bias.

### Step 7: single-trial examples (Cz)
- Picked by rule: lowest / middle / highest raw-first mu change, plus
  flagged run 10 trial 1 and run 14 trial 8.
- Single trials look very different from each other and speckly
  (±10 dB scale); none closely resembles the average (±3 dB).
- Flagged trials do not stand out; all trials look messy. Kept
  (include = True); compare with/without them in Milestone 5.
- Each trial = consistent signal + changing noise; averaging cancels
  much of the noise, so only the average shows the consistent pattern.

- Window = how much signal is used to make one slice of the map
  (1 s = 160 samples, 0.5 s = 80 samples).
- Frequency spacing = 1 / window length. To tell 10 Hz from 11 Hz you
  need to see them drift apart: in 1 s they differ by 1 full cycle,
  in 0.5 s by only half a cycle, so 0.5 s lumps them into 2 Hz rows.
- Each slice blends everything inside its window, so a shorter window
  pins down *when* a change happened more precisely.

### Milestone 4 wrap-up readings (Step 6 map, 1 s window, Cz)
- Pre-cue: rest area mostly even and pale, slightly redder toward
  -0.5 s. Possible anticipation; overlapping slices may smear one
  burst. A raised baseline would shrink, not create, the imagery
  increase. Observation only.
- Beta 13–30 Hz in imagery window: mostly red, consistent with
  Milestone 3 (beta lower in 8/24).
- Reference: per trial and frequency, mean power of 11 rest slices
  (centres -1.5 to -0.5 s = chunks fully within -2 to 0 s).


## Milestone 5 — participant selection (November 1, 2026)
- Chosen before viewing any data: participants 1,  33, 14, 79, 98 (seed 2026).
- Full shuffled order saved in data/participant_selection.csv.
- Replacement rule: a participant is replaced by the next backup only for
  data-format problems (sampling rate not 160 Hz, missing runs 6/10/14,
  missing C3/Cz/C4). Never because of how their results look.
- Frozen settings unchanged from Milestone 4.

## Milestone 5 — quality rules (decided November 1, 2026, before viewing new data)
- Main flag rule: trial flagged if Cz (filtered, average referenced) exceeds
  150 µV peak-to-peak in its rest OR imagery window. 150 µV is a common
  convention (e.g. MNE tutorials), not derived from these participants.
- Cross-check: also flag if a trial's peak-to-peak exceeds 3 × that
  participant's median trial peak-to-peak (relative rule). Reported only.
- A flag means "check", not "delete". Primary analysis keeps all trials;
  a sensitivity check repeats it without fixed-rule flagged trials.
- Same rules for all five participants, including participant 1.
- No participant is dropped for having many flags; flag counts are reported.


## Milestone 5 — step 3a format and quality check (November 2, 2026)
- All five participants (1, 33, 14, 79, 98) passed format checks: 160 Hz,
  runs 6/10/14, C3/Cz/C4 present. No replacements needed.
- Extracted trials: 24, 23, 21, 24, 24. No cues skipped; 33 and 14 have
  fewer foot-imagery cues in their recordings.
- Median Cz peak-to-peak: 110, 67, 78, 120, 38 µV (large between-person
  differences in overall amplitude).
- Fixed 150 µV flags: P1 run 10 trial 1 (matches one Milestone 2 visual flag;
  run 14 trial 8 not flagged); P79 run 10 trials 2, 7, 8 and run 14 trials
  5, 6 (all 151–172 µV, close to P79's 120 µV median).
- Relative (3 × median) flags: none for any participant.
- Interpretation: P79's flags likely reflect overall amplitude, not clear
  artifacts. All trials kept for the primary analysis; flagged trials
  dropped only in the sensitivity check.


  ## Milestone 5 — step 3b results, all trials kept (November 2, 2026)
- Frozen M4 settings; P1 reproduced M4 exactly (mu lower 7/24, +0.94 dB).
- Mu (raw-first, per trial): P1 lower 7/24 (+0.94 dB), P33 12/23 (−0.40),
  P14 16/21 (−2.68), P79 6/24 (+1.54), P98 16/24 (−3.23).
- Beta lower: P1 5/24, P33 14/23, P14 14/21, P79 8/24, P98 15/24.
- Grouping by mu count: ERD-like P14, P98; opposite P1, P79; mixed P33.
- Counts preferred over means: P98's mean is pulled by one −14.3 dB trial.
- Conclusion so far: direction of mu change at Cz is not consistent across
  participants. Uncertainty not yet quantified (bootstrap next).

- Maps: P1 and P79 mainly red in mu after 1 s; P33, P14, P98 mixed. P14/P98
  counts say mostly lower, but ratio averaging lets a few large increases
  (+6.3, +8.1 dB trials) outweigh many mild decreases, so maps look mixed.


## Milestone 5 — step 4 sensitivity check (November 2, 2026)
- Without fixed-rule flags: P1 7/23 lower (+0.83 dB, was +0.94);
  P79 5/19 lower (+1.06 dB, was +1.54). P33, P14, P98 had no flags.
- P1 without Milestone 2 visual flags (run 10 t1, run 14 t8): 7/22 lower, +0.78 dB.
- P79's removed trials: 1 lower, 4 higher. Flagged trials tended to have
  larger imagery-window swings, so removing them pulled means toward 0.
- No participant changed direction; flagged trials did not drive results.

## Milestone 5 — step 5 bootstrap, within-person uncertainty (November 2, 2026)
- 10,000 resamples of whole trials (never time slices), seed 2026, all trials.
- Mean mu dB [95% interval]; % trials lower [95% interval]:
  P1  +0.94 [+0.20, +1.66]; 29% [12, 46]  -> reliably higher
  P33 −0.40 [−1.75, +0.86]; 52% [30, 74]  -> unclear
  P14 −2.68 [−4.14, −1.07]; 76% [57, 91]  -> reliably lower
  P79 +1.54 [+0.50, +2.59]; 25% [8, 42]   -> reliably higher
  P98 −3.23 [−5.35, −1.02]; 67% [46, 83]  -> probably lower, borderline
- P98's mean interval excludes 0 but its count interval crosses 50%; the
  mean is pulled by one −14.3 dB trial. Count is the primary summary.
- Individual directions are fairly clear but differ between participants.

## Milestone 5 — step 6 participant-level summary (November 4, 2026)
- Each participant reduced to one number (mean per-trial mu change), then
  10,000 bootstrap resamples of the 5 PEOPLE (seed 2026); per-person
  intervals identical to step 5.
- 3 of 5 participants lower on average (P33, P14, P98); 2 higher (P1, P79).
- Average of person means −0.77 dB [−2.44, +0.91]; average % trials lower
  50% [32, 68]. Both cross no change. Rough: only 5 participants.
- Four participants individually exclude 0 (P1, P79 higher; P14, P98 lower),
  so the group "no change" reflects opposite directions cancelling, not
  absence of change.
- Figure: outputs/m5_participant_comparison.png



