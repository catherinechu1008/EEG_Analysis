# Milestone 5b — Does the Result Depend on the Method?

**Estimated time:** 3–5 hours
**Status:** Not started
**Builds on:** Milestone 5 (five participants, bootstrap) and Days 3–10 of the Power Spectrum Part 2 study plan
**Also completes:** Days 11 and 12 of the Power Spectrum Part 2 study plan

## Where this fits

| Milestone | Status |
|---|---|
| 1–5 | Complete |
| **5b — Method check** | **This plan** |
| 6 — Unity replay | Skipped for now (by choice); can be picked up later |
| 7 — Package the project | Next, after 5b |

## Purpose

Milestone 5 found that the direction of the mu change at Cz differs between participants (P14 and P98 lower; P1 and P79 higher; P33 unclear). Every number came from one method: 1 s Hann windows averaged across the 2 s rest and imagery windows.

This milestone asks one question: **would a different, well-justified spectral method give the same answer?** If it does, the finding is stronger. If a participant flips direction, that is a real finding too: their result is sensitive to the method.

It also produces one figure that explains the difference between two kinds of uncertainty, which matters for any future claim that a treatment "worked".

## Rules (decide before running anything)

- **The frozen Milestone 4/5 result stays the primary result.** Everything here is labeled *exploratory* or *sensitivity check*.
- **Multitaper settings are fixed now:** 2 s windows (320 samples), time-bandwidth setting NW = 2, K = 3 tapers, about ±1 Hz smoothing. Do not change them after seeing results.
- **Same trials, same participants, same windows:** all trials kept (as in step 3b of Milestone 5), rest −2 to 0 s, imagery 1 to 3 s, Cz, mu 8–13 Hz primary, beta 13–30 Hz secondary.
- **Same per-trial number:** raw-first change, `10 × log10(imagery mu power / rest mu power)`, as in Milestone 4.
- **Agreement rule (written now):** a participant "agrees" if the sign of their mean mu change is the same under both methods. Counts (trials lower / total) are reported alongside, not used to decide.

## Step 1 — Multitaper sensitivity check (about 2 hours)

**Learn:** How a multitaper estimate on the whole 2 s window differs from the Milestone 4 method.

| | Milestone 4/5 (primary) | Milestone 5b (check) |
|---|---|---|
| How the 2 s window is used | 11 overlapping 1 s slices, averaged | Whole 2 s at once |
| Taper | Hann on each slice | 3 Slepian (DPSS) tapers |
| Frequency spacing | 1 Hz | 0.5 Hz |
| Smoothing | about ±2 Hz (Hann on 1 s, Day 7) | about ±1 Hz (NW ÷ T = 2 ÷ 2 s, Day 9) |
| Noise reduction | averaging slices | averaging 3 taper spectra |

**Code:** new script `scripts/05b_multitaper_check.py`.

1. For each of the five participants (1, 33, 14, 79, 98), use `prepare_participant()` to get `trial_pairs`. Take the Cz row of `pair["rest"]` and `pair["foot"]` (320 samples each), convert to µV and subtract each segment's mean.
2. Build the tapers once: `scipy.signal.windows.dpss(320, 2, 3)`. Multiply the segment by each taper, FFT each, and compute `2 * dt * |fft|²` for each (Day 9 note: Slepian tapers are already scaled). Average the 3 power spectra (not the tapers or the tapered signals; Day 8).
3. Mu power = mean PSD over the 8–13 Hz bins. Same for beta. Then the per-trial raw-first change in dB.
4. Read `outputs/m5_trial_changes.csv` and match trials by participant, run and trial number.
5. Print a table: participant, trials, mu lower (Milestone 5 vs multitaper), mean mu dB (both), agrees yes/no. Do the same for beta.
6. Bootstrap the multitaper per-trial mu changes with the same method as `05_bootstrap.py` (10,000 resamples of whole trials, seed 2026).
7. Figure: one scatter panel per participant, x = Milestone 5 mu change, y = multitaper mu change, one dot per trial, diagonal line `y = x`, lines at 0. Dots near the diagonal mean the methods agree trial by trial.
8. Save `outputs/m5b_multitaper_changes.csv` and `outputs/m5b_method_agreement.png`.

**Sanity checks:**
- Rest compared with itself gives 0 dB.
- Multitaper and Welch-style PSDs of the same segment are in the same units (µV²/Hz) and similar in size away from peaks.

**Check:** If the two methods disagree on single trials but agree on each participant's mean, what does that say about single trials?

## Step 2 — Two kinds of uncertainty (about 1–1.5 hours)

**Learn:** Day 10's chi-square interval and Milestone 5's bootstrap interval answer different questions.

| Interval | Question it answers | What it ignores |
|---|---|---|
| Chi-square (one trial, K = 3 tapers) | How precisely did this one 2 s window measure power? | Whether the next trial would look similar |
| Bootstrap (across trials) | How much would the average change with a different set of trials? | Nothing about a single window's precision |

For a "did it help?" claim, the second question is the one that matters. A precisely measured single trial can still be unusual.

**Code:** add to the same script (or `scripts/05b_uncertainty_figure.py`).

1. Participant 1 (the reference participant). Pick the trial by rule: the median trial of the multitaper mu change from Step 1. Do not pick by how it looks.
2. **Left panel:** that trial's rest and imagery multitaper spectra in dB, 2–40 Hz, each with a 95% chi-square interval:
   lower = `2K·S / chi2.ppf(0.975, 2K)`, upper = `2K·S / chi2.ppf(0.025, 2K)`, K = 3.
   Use 0.025 and 0.975, not the chapter's 0.05 and 0.95 (Day 10).
3. **Right panel:** the mean multitaper spectrum across all of participant 1's trials, rest and imagery, each with a 95% bootstrap interval (resample whole trials, 10,000 times, seed 2026, 2.5th and 97.5th percentiles). Average power first, then convert to dB (Milestone 4 lesson).
4. Use the same y-axis range on both panels and shade 8–13 Hz.
5. Save `outputs/m5b_two_uncertainties.png`.

**Expected:** single-trial intervals are wide and rest and imagery overlap almost everywhere; the trial-average intervals are much narrower. Write down what you actually see, even if it differs.

**Limitation to state:** the chi-square interval assumes the signal is steady (stationary) over the 2 s window and roughly Gaussian. EEG bursts break this, so treat the interval as approximate.

**Check:** Why can a single-trial interval be narrow while the participant's result is still uncertain?

## Step 3 — Leakage caption for Milestone 3 (about 20 minutes)

**Learn:** Apply Days 3 and 7 to an existing figure.

The Step 2 figure in `scripts/03_compare_rhythms.py` (single-trial FFT, run 6 trial 1) uses no taper, which means a rectangular window. Your notes say power there is strongest near 1 Hz. Rectangular-window leakage falls off slowly (about 6 dB per doubling of distance), so some of that slow power can spread into 8–13 Hz.

1. Recompute that one trial's spectrum with a Hann taper (same 2 s segment, same scaling corrected for the taper).
2. Compare the two spectra in the mu band. Is the rectangular version raised there?
3. Add a one-sentence caption to the Milestone 3 notes. Do not change the Milestone 3 result: it was based on Welch with Hann tapers, not on this figure.

## Step 4 — Notes and figures (about 30–45 minutes)

Add a "Milestone 5b" section to `notes/inspection_notes.md` with:

- The agreement table (Step 1) and one bullet per participant that flipped, if any.
- Three figures, each with a 2–3 sentence caption: the method-agreement scatter, the two-uncertainties figure, and the leakage comparison.
- For each figure: the method choice, one observation, one limitation. This is Day 12 of the study plan.

## Deliverables

- `scripts/05b_multitaper_check.py` (and the optional figure script)
- `outputs/m5b_multitaper_changes.csv`
- `outputs/m5b_method_agreement.png`
- `outputs/m5b_two_uncertainties.png`
- Milestone 5b notes with three captioned figures

## Completion check

You can explain, without notes:

1. Whether each participant's mu direction survived a change of method, and what that means for how much to trust it.
2. The difference between "this measurement is imprecise" and "this result varies from trial to trial", and which one matters for judging whether an intervention changes the brain.
3. Why the multitaper settings were fixed before running, and why the Milestone 5 result stays primary even if multitaper looks "nicer".

## What not to do

- Do not switch the primary result to multitaper because it agrees better with what you expected.
- Do not try several NW values and report the one that looks best. (A different NW can be a later, separately labeled exploration.)
- Do not drop trials or participants based on these results.

## Prompt for the session

Begin Milestone 5b of Project1. Milestones 1–5 are complete; Milestone 6 is skipped for now; Milestone 7 comes after this. The user has completed Days 1–10 of the Power Spectrum Part 2 study plan (leakage, zero padding, Hann, multitaper, NW and taper count, chi-square confidence intervals). Follow the rules and steps in `Milestone_5b_Method_Check_Plan.md` in order. Reuse `prepare_participant()`, `outputs/m5_trial_changes.csv` and the bootstrap approach in `scripts/05_bootstrap.py`; do not repeat loading, filtering or extraction concepts. Explain the purpose before code, one concept at a time, with small number tables and everyday analogies. After each comparison, recap in plain words what was tried, what was found and what it means. The user pastes code themselves: give complete, clearly placed code blocks. Plots run from PowerShell: `plt.show(block=False)` per figure and one final `plt.show()`.
