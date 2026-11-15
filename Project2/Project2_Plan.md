# Project 2 — Does Rehabilitation Change the Brain's Response?

**Working title:** EEG evidence for a stroke rehabilitation add-on and for change across treatment
**Estimated effort:** 30–45 hours
**Status:** Not started. Begin after Project1 Milestones 5b and 7.
**Prepared:** November 11, 2026

## Why this project

Project1 asked: *does a brain signal respond to a task clearly enough to be useful?* Healthy volunteers imagined moving their feet, and you measured mu and beta power at Cz.

Your career goal needs the next question: *when someone receives a treatment, does the brain evidence show that something changed, and how sure can we be?* This project uses real stroke patients' EEG to practice exactly that, with three links of an evidence chain:

| Link | Question | Can this dataset answer it? |
|---|---|---|
| 1. Target engagement | Does the add-on change the brain process it is supposed to work on, right now? | **Yes.** Same patients, with and without the add-on |
| 2. Change over treatment | Is that brain response different after treatment than before? | **Partly.** Pre, post and follow-up recordings exist, but there is no control group |
| 3. Clinical meaning | Do patients whose brain response changed also move better? | **No.** No motor scores are published. You will write down what would be needed |

Knowing where the evidence stops is part of the skill. For VR therapy for rehab, mental health or addiction, the same three links apply: swap "electrical stimulation" for "VR embodiment" or "VR exposure" and the design questions stay the same.

## Dataset

**Lower limb motor imagery EEG dataset based on the multi-paradigm and longitudinal-training of stroke patients** (Scientific Data, 2025, volume 12, article 314).

- Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11845778/ (DOI 10.1038/s41597-025-04618-4)
- Data: Figshare, BIDS format (link in the paper's Data Records section). A third-party BIDS re-host exists at https://zenodo.org/records/18987384; prefer the original.

What the paper reports (verify everything in Milestone 1):

- 27 stroke patients (1–12 months after stroke), imagining walking with the **affected leg**. This connects directly to Project1's foot imagery and Cz.
- Each trial is about 12 s: fixation cross 0–3 s → cue text at 3 s → imagery **or** idle (clear mind) 4–9 s → relax 3 s. 40 imagery and 40 idle trials per experiment, in random order.
- **Paradigm experiments:** conventional imagery, and two "sensory-enhanced" versions with electrical stimulation of the affected leg during the task: constant (IES) and gait-phase-matched (SES). Idle trials appear to include the stimulation too ("ignoring stimulation"); confirm this.
- **Longitudinal experiments:** the conventional paradigm recorded at pre-treatment, post-treatment and follow-up.
- Each patient did at least three experiments, either the paradigm set or the longitudinal set (see the paper's Table 1).
- 64 channels, recorded at 1000 Hz. Preprocessed files: 40 channels, 250 Hz, 3–35 Hz band-pass, common average reference, ICA cleaning, segmented. EEGLAB `.set` format (MNE can read these).
- Not reported: healthy controls, a no-treatment control group, motor scores (such as Fugl-Meyer), or a description of the treatment between sessions.

**Backup if this dataset does not work out:** "A multi-paradigm and longitudinal EEG dataset including the 'sixth-finger' and 'affected-hand' motor imagery of stroke patients" (Scientific Data, 2026), https://pmc.ncbi.nlm.nih.gov/articles/PMC13424360/. It has a similar design for the upper limb; check its contents before switching.

## Questions

**Primary (A), target engagement:** In the same patients, is the imagery-specific mu decrease at Cz larger with sensory stimulation (IES or SES) than with conventional imagery?

**Secondary (B), change across treatment:** In patients with all three time points, is the imagery-specific mu change at post-treatment or follow-up different from pre-treatment by more than the measurement's normal variation?

## The key new measure: "imagery-specific" change

In Project1, imagery was compared with rest before the cue. That is not enough here. During IES and SES the leg is being stimulated, and stimulation alone changes sensorimotor rhythms. A bigger decrease could come from the stimulation, not from imagery.

The fix is to use the idle trials as a built-in control:

| Trial type | What it contains | Change from pre-cue fixation |
|---|---|---|
| Imagery | Cue + stimulation (if any) + **imagining** | example: −3.0 dB |
| Idle | Cue + stimulation (if any) | example: −1.0 dB |
| **Imagery-specific change** | Imagery minus idle | **−2.0 dB** |

Per patient and per experiment: imagery-specific change = mean imagery-trial dB change − mean idle-trial dB change. Imagery and idle trials are different trials, so they are not paired. The bootstrap resamples each group separately.

## Analysis choices to freeze in Milestone 2 (candidates)

| Choice | Candidate | Reason |
|---|---|---|
| Channel | Cz primary; neighbours exploratory | Leg area sits near the midline; same as Project1 |
| Band | Mu 8–13 Hz primary, beta 13–30 Hz secondary | Same as Project1 |
| Baseline window | Fixation 1–3 s of each trial (2 s, before the cue text) | Avoids the visual response to the cue (Project1 lesson) |
| Task window | 5–7 s (1–3 s after task onset, 2 s) | Mirrors Project1's +1 to +3 s; equal length to the baseline |
| Spectral method | Multitaper, 2 s windows, NW = 2, K = 3 (about ±1 Hz) | Uses Power Spectrum Part 2; equal windows mean identical settings |
| Per-trial number | Raw-first: 10 × log10(task mu / baseline mu) | Project1 Milestone 4 lesson |
| Within-patient uncertainty | Bootstrap whole trials, 10,000 resamples, fixed seed | Same as Project1 |
| Between-patient summary | One number per patient, then bootstrap patients | Same as Project1 |

**Decision point:** the paper says its ERSP baseline was 1 s before task onset, which may mean the preprocessed segments do not include the fixation period. If they don't, either use the raw `_ori.set` files with your own Project1-style preprocessing (more work), or use a shorter baseline and record the cue overlap as a limitation. Decide in Milestone 1, before looking at any outcomes. If using raw files, apply Project1 preprocessing only (band-pass filter + average reference, no ICA). Handle noisy trials with the quality flags and the sensitivity analysis, and record remaining noise as a limitation.

## Milestones

### 1. Understand the dataset (5–7 hours)

- Download the data (script, not by hand) and confirm the license allows your use and any sharing of derived data.
- Learn the BIDS folder layout and load one raw and one preprocessed `.set` file with MNE.
- Verify: sampling rates, channel names (is Cz in the preprocessed 40?), units, event codes, imagery vs idle labels, segment start and end times, whether idle trials include stimulation.
- Make a **session table**: patient, affected side, months since stroke, which experiments exist (conventional / IES / SES / pre / post / follow-up), trial counts. Note sub-03 and sub-08 (20 trials per task in IES) and any missing information.
- Count how many patients have all three paradigms and how many have all three time points. These are your real sample sizes.
- Look only at format and trial counts, **not** at any power or ERD results.

**Deliverable:** session table CSV, dataset notes, the baseline decision.
**Completion check:** you can say exactly what each file contains and which patients answer which question, without guessing.

### 2. Write and freeze the analysis plan (2–3 hours)

This is a small "pre-registration": writing down the analysis before seeing outcomes, as clinical trials do.

- Fill in the frozen-choices table above (final values).
- Write the primary and secondary questions, the patient lists for each, and what result would count as "larger", "smaller" or "unclear" (for example: the patient-level 95% bootstrap interval excludes 0).
- Write the quality rules (peak-to-peak threshold plus a relative cross-check, flag means "check", not "delete"; sensitivity analysis without flagged trials), as in Project1.
- Commit the plan to git with a date before running Milestone 3.

**Deliverable:** `analysis_plan.md`, committed.
**Completion check:** someone else could run your analysis from the plan alone.

### 3. Build the measure on one patient (5–7 hours)

- Choose the development patient by rule (for example, the lowest-numbered patient with all three paradigms), not by data.
- Build `project2/` modules in the same style as Project1's `eeg_rehab/`: data loading, trial extraction, multitaper band power, imagery-specific change, bootstrap.
- Sanity checks: baseline vs itself gives 0 dB; units µV²/Hz; trial counts match the session table; idle-trial change looks plausible.
- Plot one cue-aligned time–frequency change map for imagery and one for idle (exploratory, display only).
- Do not change frozen settings because of this patient's results. Fix only bugs.

**Deliverable:** working pipeline, one patient's results and figures.
**Completion check:** you can explain why the idle trials are subtracted and what the result would mean without them.

### 4. Question A — Does the add-on engage the target? (6–9 hours)

- Run the frozen analysis on every patient with all three paradigms.
- Per patient: imagery-specific mu change for conventional, IES and SES, each with a bootstrap interval.
- Per patient: enhanced minus conventional (IES − conventional, SES − conventional).
- Across patients: bootstrap of patient differences; count of patients where enhanced is more negative.
- Sensitivity checks: without flagged trials; beta band; without idle subtraction (to show how much the stimulation alone would have inflated the effect).
- Report every patient, including opposite and unclear results.

**Deliverable:** paradigm comparison figure (one row per patient), results and limitations notes.
**Completion check:** you can separate "stimulation changed the EEG" from "stimulation changed the imagery response", and explain why the second is the claim that matters.

### 5. Question B — Change across treatment (6–9 hours)

**New concept: measurement noise floor.** If you measured the same person twice with no treatment, the number would still change. A treatment-related change has to be bigger than that.

- Estimate the noise floor within each session: split trials into odd and even halves, compute the imagery-specific change for each half, and look at the differences across patients. This underestimates real session-to-session noise (the cap is replaced between sessions, mood and fatigue differ), so treat it as a minimum.
- Per patient: imagery-specific mu change at pre, post and follow-up, with bootstrap intervals; post − pre and follow-up − pre.
- Across patients: bootstrap of patient-level changes; count of patients whose change exceeds their own noise floor.
- Plot one line per patient across the three time points (like Project1's paired-trial plots).

**Interpretation rules:**
- There is no control group, so a change **cannot** be attributed to treatment. Alternatives: natural recovery (strong in the first months after stroke), practice with the task, different cap placement, time of day.
- A more negative mu change is not automatically "better". Without motor scores, it is a brain change, not an improvement.

**Deliverable:** longitudinal figure, noise-floor table, results and limitations notes.
**Completion check:** you can explain why "ERD got stronger after treatment" is not evidence that the treatment worked, and what extra data would make it evidence.

### 6. Package and write "what a real study would need" (4–6 hours)

- README: questions, dataset attribution and download script, setup, reproduction steps, findings, limitations.
- Four or five figures with captions.
- A one-page section, **"From this analysis to evidence that a VR therapy works"**, covering:
  - control group or sham condition, randomization, blinded assessors
  - several baseline sessions to measure the real test–retest noise
  - a pre-registered primary EEG measure plus a clinical outcome (for example lower-limb Fugl-Meyer)
  - whether the EEG change predicts clinical change
  - why a larger noise floor means more patients are needed (qualitative only; a formal sample-size calculation is out of scope)
  - how this design maps to a VR rehab, mental health or addiction study (for example VR exposure with craving ratings and cue-reactivity EEG)
- Run everything from a clean environment in order.

**Deliverable:** reproducible repository and short case study.
**Completion check:** a reader understands what was found, what can and cannot be claimed, and what the next real study would look like.

## What carries over from earlier work

| Earlier work | Use in Project 2 |
|---|---|
| Power Spectrum Part 2: tapers, multitaper, NW | Primary spectral method on equal 2 s windows |
| Power Spectrum Part 2: chi-square intervals | Explaining single-trial precision vs between-trial variation |
| Project1 M2: trial table, quality flags | Session table, quality rules, sensitivity analysis |
| Project1 M4: raw-first dB, ratio-averaged maps | Per-trial number and display maps |
| Project1 M5: freeze before viewing, bootstrap, participant-level summary | Pre-registration, within- and between-patient uncertainty |
| Project1 M5b: method sensitivity check | Same idea, applied to idle subtraction and band choice |

## What is out of scope

- Classification or decoding (the paper already reports a CSP-SVM baseline).
- Connectivity, source localization, or deep learning.
- Your own ICA or other artifact-removal methods beyond quality flags.
- Formal sample-size (power) calculations.
- Comparing patients with healthy people (Project1's participants used a different system, task and preprocessing, so a comparison would mostly reflect those differences).
- Any claim that a treatment improves recovery.

## Suggested portfolio claim

Analyzed stroke patients' motor imagery EEG to test whether a sensory add-on strengthens the imagery-specific brain response and whether that response changes across treatment, with pre-registered measures, uncertainty estimates, and an explicit account of what the data can and cannot show.

## Prompt for the first session

Begin Project 2, Milestone 1. The user finished Project1 (PhysioNet foot imagery, Cz, mu/beta, Welch and spectrograms, raw-first dB, bootstrap, five participants, multitaper sensitivity check) and the Power Spectrum Part 2 study plan. Follow `Project2_Plan.md`. In Milestone 1, look only at format, labels, timing and trial counts; do not compute or show any power or ERD results before Milestone 2 is committed. Define every new term (BIDS, EEGLAB `.set`, pre-registration, noise floor, target engagement) before using it. Explain the purpose before code, one concept at a time, with small number tables and everyday analogies. After each step, recap in plain words what was tried, what was found and what it means. The user pastes code themselves: give complete, clearly placed code blocks. Scripts run from PowerShell: `plt.show(block=False)` per figure and one final `plt.show()`.
