# Coupled Rhythms (Coherence) — 12-Day Study Guide

*Reusable context + daily schedule + completion criteria*

**Source:** Mark Kramer & Uri Eden, *Case Studies in Neural Data Analysis*, Chapter 5: Analysis of Coupled Rhythms — https://mark-kramer.github.io/Case-Studies-Python/05.html
**Pace:** 30–40 minutes per day (about 6–8 hours total)
**Follows:** Power Spectrum Part 2 (Chapter 4), 12-Day Study Plan

## Purpose and learning context

This is a self-contained handoff document for starting a new chat each study day. The learner is an experienced Python/software developer and VR rehabilitation developer with a computer science background, studying introductory neuroscience and computational neuroscience. Long-term interests include EEG/neural data analysis, computational models of cognition, and evaluating VR motor rehabilitation and attention interventions. Teach neuroscience and statistical concepts gently; do not assume prior expertise beyond what is listed under "Carried over from Chapter 4."

This chapter asks whether rhythms recorded at **two electrodes** are coupled. The data are ECoG (electrodes on the brain's surface, not the scalp) from a patient with epilepsy during presurgical monitoring. The patient listened to phonemes and pressed a button for "ba"; both electrodes sit over auditory cortex. The file `ECoG-1.mat` contains `E1` and `E2`, each of shape (100, 500): 100 trials × 500 samples, 1 s per trial at 500 Hz, plus a time vector `t`.

The chapter's main story: both electrodes show a strong ~8 Hz rhythm and a weaker ~24 Hz rhythm. Single-trial cross-covariance makes them look coupled at 8 Hz, but coherence shows the consistent relationship is at **24 Hz**, not 8 Hz. The 8 Hz phases are scattered across trials; the 24 Hz phase differences cluster near 0. The lesson: **large amplitude does not imply large coherence.**

### Carried over from Chapter 4 (no need to re-teach)

- Spectrum scaling `2*dt**2/T * |X|**2`, decibels, frequency resolution `df = 1/T`, Nyquist `fs/2`.
- Rectangular vs Hann tapers, leakage, zero padding.
- Multitaper idea (average power spectra from several Slepian tapers), the time-bandwidth knob, chi-square confidence intervals.

## Current progress — updated November 11, 2026

DAYS 1–12 — NOT STARTED. Next: Day 1 — Meet the two-electrode data.

## Teaching agreement for every new chat

- First ask which day the learner wants to work on, unless they explicitly say it. Read that day's objective below and do not jump ahead.
- Teach in small chunks, one idea at a time. Go deeper than bullet points, but don't deliver the whole day at once. Explain why a calculation exists before syntax or formulas. Assume basic Python familiarity.
- Use clear, conversational language and small worked examples (toy signals with known answers) before applying a method to the ECoG data.
- Give a short explanation/practice and a few concept checks. Accept concise numeric and code answers; do not require written explanations when the answer and existing context demonstrate understanding. Review answers one by one. Default to brief correctness feedback and the correct answer for errors. Give hints when requested.
- Mark a day complete only after the learner demonstrates the specific completion criteria. If concepts remain weak, ask at most a few focused follow-ups, not an endless quiz.
- Do not imply that coherence shows direction, causation, or a direct anatomical connection. Coherence measures how consistent the phase relationship is across trials at one frequency.
- After each day, provide a concise progress update that can be pasted into this document: day number, complete/in progress, what was learned, open confusions, and suggested next day.

## The 12-day schedule

Days 1–10 follow the chapter in order. Days 11–12 apply and consolidate. Each day lists **Work** (what to do), **Scope** (what is in and out today), and a **Completion check**.

### Day 1 — Meet the two-electrode data

**Estimated time:** 35–40 minutes
**Work:** Read *Introduction* (Background, Case Study Data). Download `ECoG-1.mat` from the book's `matfiles` folder into `data/` (it is not the same file as Chapter 4's `04_ECoG-1.mat`). Load it, list `data.keys()`, and check shapes of `E1`, `E2`, `t`. Derive `dt`, `fs`, `T`, `N`, and `K` (number of trials). Plot trial 1 of `E1` and `E2` on the same axes. Then make an `imshow` image of all trials for each electrode and plot the first four trials.
**Scope:** In: loading, shapes, reading plots by eye. Out: the on-ramp coherence code (optional to run just to see the end goal, but do not study it yet); any covariance or spectra.
**Completion check:** State what rows and columns of `E1` represent and give fs, T, N, K. Read an `imshow` image (what rows, columns, and color mean). Estimate the dominant rhythm by counting cycles (~8 Hz), and say whether its peaks line up across trials.
**Status:** Not started.

### Day 2 — Autocovariance refresher

**Estimated time:** 30 minutes
**Work:** Compute the autocovariance of one trial of `E1` with `np.correlate(x, x, 'full') / N` after removing the mean. Build the lag axis. Then average autocovariances over all 100 trials and plot against lag (±0.2 s is enough).
**Scope:** In: autocovariance only, for one electrode. Out: cross-covariance (Day 3).
**Completion check:** Give the length of the `'full'` output (2N − 1 = 999) and what the middle index means. Explain why lag 0 is the largest value. Convert the side peaks at ±0.125 s into a frequency.
**Status:** Not started.

### Day 3 — Single-trial cross-covariance

**Estimated time:** 35–40 minutes
**Work:** Read *Cross-covariance*. First build a toy: make `x` a sine wave and `y` a copy delayed by a known amount, compute `np.correlate(x, y, 'full')`, and record which sign of lag the peak lands on. Then compute the cross-covariance of `E1` and `E2` for one trial and locate the largest peak (~0.04 s) and nearby trough.
**Scope:** In: one trial, interpreting lags. Out: trial averaging (Day 4).
**Implementation note:** The lag sign convention of `np.correlate` is easy to get backwards. Trust the toy example over memory before saying which electrode "leads."
**Completion check:** Using the toy result, interpret the sign of the ECoG peak lag. Explain why the cross-covariance looks periodic whenever both signals contain the same rhythm, even if they are unrelated.
**Status:** Not started.

### Day 4 — Trial-averaged cross-covariance

**Estimated time:** 30 minutes
**Work:** Loop over all trials, compute each cross-covariance, and average. Plot single-trial and trial-averaged results on the same axes; compare their sizes (the average is roughly 10× smaller). Optional: rewrite the loop with `zip` and a list comprehension.
**Scope:** In: what averaging does to cross-covariance. Out: frequency-domain explanation (Days 6–9).
**Completion check:** Explain why averaging shrank the cross-covariance (single-trial peaks fall at different lags/signs across trials and cancel). Explain why this does not yet prove "no coupling at any frequency."
**Status:** Not started.

### Day 5 — Fourier coefficients have amplitude and phase

**Estimated time:** 35–40 minutes
**Work:** Read the start of *Trial-Averaged Spectrum* (Fourier transform, polar form). Make a toy sine with a known amplitude and phase, take `np.fft.rfft`, and find its frequency bin. Use `np.abs` and `np.angle` on that coefficient. Picture each coefficient as an arrow: length = amplitude, direction = phase. Relate this to `S = 2*dt**2/T * A**2`.
**Scope:** In: the complex number as an arrow; `abs`, `angle`, radians ↔ degrees. Out: Euler's formula beyond intuition; coherence.
**Completion check:** Given a complex number, find its amplitude and phase. Shift the toy sine's phase and predict what changes in the coefficient (direction) and what doesn't (length). State which part the power spectrum keeps and which it throws away.
**Status:** Not started.

### Day 6 — Trial-averaged spectra of both electrodes

**Estimated time:** 30–35 minutes
**Work:** `rfft` each trial of `E1` and `E2`, compute power with the Chapter 4 scaling, average over trials to get `Sxx` and `Syy`, and plot in dB from 0–50 Hz. Find the peaks (~8 Hz and ~24 Hz).
**Scope:** In: power spectra only. Out: cross-spectrum (Day 8).
**Completion check:** Report both peak frequencies, `df`, and Nyquist. Explain why averaging power over trials does not cancel the 8 Hz rhythm, while averaging cross-covariance on Day 4 did (power is never negative; phase is discarded).
**Status:** Not started.

### Day 7 — Coherence intuition: arrows that line up

**Estimated time:** 35–40 minutes
**Work:** Read *Introduction to the Coherence* (both simple scenarios). For each trial, the phase difference is Φ = φ − θ. Simulate K = 100 unit arrows `np.exp(1j*Phi)`: (a) all Φ equal to the same value, (b) Φ random over [−π, π]. Compute `abs(mean(...))` for each and draw the arrows.
**Scope:** In: the equal-amplitude formula κ = (1/K)|Σ exp(iΦₖ)|. Out: the full formula with amplitudes (Day 8).
**Completion check:** Explain why κ = 1 when Φ is constant, even if Φ ≠ 0. Explain why random Φ gives a value near 0. Note that with K = 100 random phases, κ comes out around 0.09, not exactly 0 (small samples leave a little leftover length).
**Status:** Not started.

### Day 8 — Cross-spectrum and computing the coherence

**Estimated time:** 35–40 minutes
**Work:** Read *Cross-Covariance and Cross-Spectrum* and *Computing the Coherence*. Compute the trial-averaged cross-spectrum `Sxy = scale * mean(X * conj(Y))`. **Before running it**, write a prediction for where coherence will be high, based on Days 1–6. Then compute `cohr = abs(Sxy) / (sqrt(Sxx) * sqrt(Syy))` and plot 0–50 Hz. Now compare with the chapter's on-ramp code.
**Scope:** In: the full coherence formula; cross-spectrum as the frequency-domain partner of cross-covariance (concept only). Out: phase histograms (Day 9).
**Completion check:** Explain what `conj` does here (it turns two phases into a phase difference). Report where coherence peaks (~24 Hz) and contrast it with where power peaks (~8 Hz). Compare the result with your written prediction.
**Status:** Not started.

### Day 9 — Phase differences across trials

**Estimated time:** 30–35 minutes
**Work:** Read *Visualizing the Phase Difference across Trials*. Find the 8 Hz and 24 Hz indices with `np.where(f == 8)`. For each trial, compute the single-trial cross-spectrum at those frequencies and its phase with `np.angle`. Plot histograms with 20 bins over [−π, π].
**Scope:** In: linking the histograms to the Day 8 coherence values. Out: new methods.
**Implementation note:** The chapter text's degree range for the 24 Hz cluster appears garbled. Read the range from your own histogram and convert radians to degrees yourself.
**Completion check:** Describe both histograms and use them to explain the coherence result. Restate "large amplitude does not imply large coherence" in your own words with this dataset as the example.
**Status:** Not started.

### Day 10 — Single-trial coherence and the modeling link

**Estimated time:** 35–40 minutes
**Work:** Read *Single-Trial Coherence*. Compute coherence using only one trial (K = 1) and show it equals 1 at every frequency; explain why with the Day 7 arrows. Review the two fixes: (1) split one long recording into segments treated as trials (cost: coarser frequency resolution), (2) multitaper, where each taper acts like a trial (links to Chapter 4 Days 8–9). Skim *Relation between Statistical Modeling and Coherence*: coherence is a scaled version of a frequency-domain regression coefficient.
**Scope:** In: why K = 1 fails, the cost of each fix, the modeling link as a concept. Out: deriving the regression formulas.
**Completion check:** Explain why one trial always gives coherence 1. Compute the frequency resolution if a 1 s trial is split into four 0.25 s segments (4 Hz). Name one cost of each fix.
**Status:** Not started.

### Day 11 — Apply it to your EEG project

**Estimated time:** 35–40 minutes
**Work:** Choose two channels from your own EEG data (for example, two motor-area channels) and a set of equal-length, event-aligned trials from one condition. Compute trial-averaged spectra and coherence with identical settings. If time allows, compare two conditions (e.g., rest vs imagery) using the same channels, window length, and trial count.
**Scope:** This is a practice analysis, not a finding. Use many trials (coherence with few trials is biased upward; see Day 7). Keep window length and trial count equal across conditions.
**Implementation note:** Scalp EEG coherence between nearby channels can be inflated by volume conduction and the shared reference (one source picked up by both electrodes, at near-zero phase difference). Mention this when interpreting; do not treat high scalp coherence as proof of two brain areas communicating.
**Completion check:** Name the settings that must match for a fair comparison. Report one observation and one reason it might not reflect true coupling.
**Status:** Not started.

### Day 12 — Build a mini notebook

**Estimated time:** 35–40 minutes
**Work:** In one notebook: load the data, show the ~8 Hz rhythm by eye, cross-covariance (single vs averaged), spectra, coherence, and the 8 vs 24 Hz phase histograms. Write two or three sentences under each figure.
**Scope:** Reuse earlier code; no new methods.
**Completion check:** Produce an understandable notebook and explain the method choice, the main finding (coherent at 24 Hz, not 8 Hz), and one limitation.
**Status:** Not started.

## Reusable new chat prompt

> I am following the attached Coupled Rhythms 12-Day Study Guide, based on Chapter 5 of Case Studies in Neural Data Analysis (https://mark-kramer.github.io/Case-Studies-Python/05.html). Please read the context, schedule, and progress section. Today I am working on DAY [NUMBER]. Teach only this day's material in small chunks, one idea at a time, using short explanations and Python examples, then quiz me against its completion criteria. Accept concise numeric and code answers; do not require extra written explanations when understanding is clear. Evaluate answers one by one with brief correctness feedback and correct answers for errors. Give hints when I ask for them. At the end, decide whether this day is complete and produce a short progress update I can save for the next chat. My current baseline: no days completed; Day 1 — Meet the two-electrode data — is next unless I update it.
>
> IMPORTANT: Present the exam and follow-up questions with answer input boxes, optional collapsible hints, and a submission action when available, as specified in the Daily exam presentation and evaluation protocol. Do not display answer keys before I respond.

## Reusable daily progress update template

- Date: ______   Day: ______   Status: Complete / In progress
- Topics practiced: ______
- What I can explain or do without help: ______
- What I still find confusing: ______
- Next recommended activity: ______

## Reference and limitations

Primary reading: https://mark-kramer.github.io/Case-Studies-Python/05.html. This guide is a learning scaffold, not a transcription of the chapter. Use the chapter's actual code and data as the source of truth, but check its labels against your own output (as with the Chapter 4 confidence-interval labeling). Keep in mind:

- Coherence measures phase consistency across trials at one frequency. It does not show direction, causation, or a direct connection.
- Coherence estimates are biased upward when there are few trials; they are undefined (always 1) for a single trial without segmenting or tapers.
- Scalp EEG adds volume conduction and reference effects that ECoG largely avoids; real motor-task EEG also needs artifact handling and careful controls.

## Daily exam presentation and evaluation protocol

Apply this consistently for every day, adapting questions to that day's material.

### 1. Start with a clear quiz header

Use "Day N Quiz: [topic]", the chapter name, today's learning objective, and an explicit completion checklist. Keep scope limited to that day. Usually 5–8 short conceptual questions plus a 2–4-part coding or application exercise where relevant.

### 2. Make it feel like an interactive exam

Show each question as its own numbered block with a place to type an answer. Use answer input boxes for both the initial exam and follow-up questions whenever interactive UI is available. Include an optional "Need a hint?" control that hides the hint at first. Otherwise provide numbered questions, visible answer spaces, and optional hints without giving away solutions.

### 3. Include approachable practice

For Python days, show a very small self-contained example (e.g., three unit arrows, a 4-sample signal) and ask the learner to predict output, explain indexing, modify a line, or interpret a plot. For conceptual days, include an applied question involving EEG or VR rehabilitation. Stay within the material taught that day.

### 4. Allow a single submission for review

If supported, show progress such as "7/11 answered" and a "Submit answers for evaluation" control that sends the numbered question-and-answer text into the chat. Do not require every field to be answered; flag blanks during review.

### 5. Grade question by question, not just by a total score

Evaluate each response individually. Accept concise numeric and code answers when correct. Default to brief Correct / Wrong feedback and the correct answer for errors. Use Correct / Mostly correct / Partially correct / Needs revision only if the learner asks. Explain a misunderstanding briefly only when useful or requested.

### 6. Give hints or direct corrections as requested

Default to direct correction: say whether each answer is right or wrong and give the correct answer for errors. If the learner asks for hints before solutions, do that instead. Do not withhold an answer after they ask for it.

### 7. Finish with a short mastery check

Use no more than 1–3 targeted follow-up questions for remaining gaps, with answer boxes when supported. Mark the day COMPLETE when the learner meets its completion criteria. Avoid repeated explanation requests and endless probing. Clearly distinguish COMPLETE and IN PROGRESS.

### 8. End with a portable handoff

Give a copy-ready progress summary with date, day, status, mastered concepts, remaining gaps, and next step. Do not assume a new chat remembers the day's answers; the learner may paste this summary into the guide.

### Quiz styling example (text fallback)

> **Day 7 Quiz: Coherence Intuition**
> Objective: Explain why lined-up phase differences give high coherence.
>
> **Question 1.** Three trials have phase differences 0.5, 0.5, 0.5 rad. What is κ?
> [Your answer: ____________________]
> *Hint (optional): Do the arrows point the same way?*
>
> **Question 2.** Why doesn't the value 0.5 itself matter?
> [Your answer: ____________________]
>
> Submit your answers for brief question-by-question feedback. Ask for hints if you prefer them before corrections.
