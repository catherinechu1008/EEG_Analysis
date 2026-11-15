# Project1 Wrap-Up Plan

**Started:** November 14, 2026
**Goal:** Make sure I understand the core concepts, finish the written results
and limitations, and package the project so someone else can understand and
rerun it.
**Skipped (by choice):** Milestone 6, the Unity replay. It can be added later.

| Part | What | Status |
|---|---|---|
| A | Concept recap | In progress (concepts 1–5 done) |
| B | Results and limitations write-up | Not started |
| C | Milestone 5b method check | Optional, decide after B |
| D | Package the project | Not started |

---

## Part A: Concept recap

**Why:** I need to be able to explain every step in my own words before I
write it up or present it.

**How:** one concept at a time, each with a short check question (number
questions where possible). After each one, a short section is added to
`notes/concept_recap.md`.

| # | Concept | Where it was used | Done |
|---|---|---|---|
| 1 | The question; rest vs imagery windows; ERD vs ERS | Milestones 1–2 | [x] |
| 2 | Filtering (1–40 Hz, zero-phase) and average reference | Milestone 2 | [x] |
| 3 | Spectra: FFT, Welch, bin spacing, Nyquist | Milestone 3 | [x] |
| 4 | Band power; why count trials instead of trusting one trial | Milestone 3 | [x] |
| 5 | Decibels; why average ratios first and convert to dB last | Milestone 4 | [x] |
| 6 | Time–frequency maps; the window-length trade-off | Milestone 4 | [ ] |
| 7 | Freezing settings and quality rules before seeing new data | Milestone 5 | [ ] |
| 8 | Bootstrap: within one person vs across people | Milestone 5 | [ ] |
| 9 | What the result can and can't claim | Milestone 5 | [ ] |

**Done when:** I can explain each concept without notes, and
`notes/concept_recap.md` has all 9 sections.

---

## Part B: Results and limitations

**Why:** the Milestone 5 deliverable asks for results and limitations
sections. Right now the findings only exist as step-by-step notes in
`notes/inspection_notes.md`, and `notes/milestone5_results.md` is empty.

**How:**
1. Claude drafts `notes/milestone5_results.md` from my notes.
2. I read every sentence and check I could defend it if someone asked "why?".
   Anything I can't explain goes back to Part A.

**Results section should cover:**
- What was analysed: 5 participants chosen at random in advance, Cz, mu
  8–13 Hz, rest −2 to 0 s vs imagery 1 to 3 s, settings frozen after
  Milestone 4.
- Each participant's result: trials lower, mean dB change and bootstrap
  interval.
- The sensitivity check: removing flagged trials didn't change any direction.
- The across-people summary: no consistent group direction, because opposite
  directions cancel (4 of 5 people individually show a clear change).

**Limitations section should cover:**
- Only 5 participants, so the group-level interval is rough.
- One electrode, one band and one window, so other sites or timings could
  differ.
- Possible alternative explanations: visual cue effects, anticipation before
  the cue, artifacts that weren't confirmed or removed.
- Zero-phase filtering is offline only, so this says nothing about real-time
  feedback.
- An EEG change is not evidence of rehabilitation benefit.

**Done when:** `notes/milestone5_results.md` is written and I agree with
every sentence.

---

## Part C: Milestone 5b method check (optional)

**What:** rerun the analysis with a different spectral method (multitaper,
settings fixed in advance) and check whether each person's direction stays
the same. Full plan: `Milestone_5b_Method_Check_Plan.md`.

**Why it's optional:** the project is presentable without it. Doing it makes
the result stronger ("the finding doesn't depend on one method") and finishes
Days 11–12 of the Power Spectrum Part 2 study plan.

**Connection to the Power Spectrum Part 2 study plan**
(`../Power Spectrum Part 2 learning/`):

| 5b step | Uses study plan days | Concept |
|---|---|---|
| Step 1: multitaper check | Day 7, Day 8, Day 9 | Hann smoothing; average the power spectra of 3 Slepian tapers; NW = 2 gives about ±1 Hz smoothing on 2 s |
| Step 2: two kinds of uncertainty | Day 10 | Chi-square interval with 0.025 / 0.975 cut-offs, K = 3 |
| Step 3: leakage caption | Day 3, Day 7 | Rectangular-window leakage (about 6 dB per doubling of distance) |
| Step 4: notes and figures | Day 12 | Method choice, one observation, one limitation per figure |
| Whole milestone | Day 11 | Apply the method to my own EEG with identical settings for rest and imagery |

**Decide after Part B:** do it now, later, or skip.

---

## Part D: Package the project

**Why:** someone else (a reviewer or employer) should understand the project
and be able to rerun it without me explaining it out loud.

**Steps:**

1. **Save the figures.** Right now only Milestone 5 saves a figure
   (`outputs/m5_participant_comparison.png`). Scripts 01–04 only display
   figures, so add `savefig` lines for the ones I choose.
2. **Choose 4–5 figures and write a 2–3 sentence caption for each.**
   Candidates:
   - a raw rest vs imagery example (Milestone 1)
   - band power per trial (Milestone 3)
   - the average time–frequency change map (Milestone 4)
   - single-trial examples next to the average (Milestone 4)
   - the participant comparison (Milestone 5)
3. **Write `README.md`:** question, dataset (PhysioNet EEG Motor
   Movement/Imagery, downloaded automatically by MNE), setup, how to run the
   scripts in order, main findings, limitations, and dataset attribution.
4. **Write a short case study** (about one page): what I asked, what I did,
   what I found, what I'd do next.
5. **Clean up:**
   - `vr_rehab.py` (old single-file version, replaced by `eeg_rehab/` and
     `scripts/`): delete it or move it to an `archive/` folder.
   - Delete the `__pycache__/` folders and add a `.gitignore`.
   - Add `scipy` to `requirements.txt` (it's used but not listed).
   - Decide whether the duplicate `trial_table.csv` at the top level is
     needed (`outputs/trial_table.csv` is the real one).
6. **Check reproducibility:** run every script in order from a fresh start and
   confirm the numbers match my notes (e.g. P1 mu lower in 7/24, +0.94 dB).

**Done when:** a stranger could read the README, run the scripts and get
the same figures and numbers.

---

## Rules for the whole wrap-up

- Don't change any frozen setting or result to make the story look better.
- Weak or mixed results are still valid findings. Report them honestly.
- Don't claim live brain control, reliable decoding or rehabilitation benefit.
