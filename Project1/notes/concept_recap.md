# Concept recap: Project1

Core ideas behind the project, in plain language. One section per concept.

---

## 1. The question and the comparison

**Question:** when someone imagines moving their feet, does the mu rhythm
(8–13 Hz) at Cz (top of the head, over the leg area) change?

- **ERD** = power goes **down** compared with rest (the textbook expectation).
- **ERS** = power goes **up** compared with rest.

```
      rest window                 imagery window
   |-------------|    gap    |-------------|
  -2 s          0 s   1 s   1 s           3 s
                 ↑ cue
```

- **Rest is taken just before the same cue**, so electrode contact, tiredness
  and eye state match the imagery window. (An eyes-closed baseline would have
  much stronger alpha at 8–13 Hz and create a fake drop.)
- **0–1 s is skipped** because the brain is still reacting to the cue on screen.
- Each trial is compared with **itself**.

---

## 2. Filtering (1–40 Hz, zero-phase)

**Why:** the raw signal contains junk that is bigger than the mu change.

| Removed | Source |
|---|---|
| below 1 Hz | slow drift (sweat, electrodes settling) |
| above 40 Hz | muscle noise, 60 Hz power-line hum |

Mu (8–13 Hz) and beta (13–30 Hz) are safely inside 1–40 Hz.

**How (the idea):** a filter is a weighted average that slides along the
signal. Averaging cancels fast wiggles; subtracting a long, heavy average
removes slow drift. MNE combines both into one set of weights. I only choose
the range (1–40 Hz).

**Zero-phase = how the filter is applied, not a separate step.** It averages
equally **before and after** each point, so **nothing shifts in time**.

| | Zero-phase (mine) | Past-only |
|---|---|---|
| Timing | correct | comes out late (about 1.65 s for my filter) |
| Needs future data? | yes | no |
| Use for | finished recordings | live feedback |

**Why it matters:** with a 1.65 s delay, the "imagery" window would actually
contain mostly rest. Zero-phase keeps the windows lined up with the cue.

**Limitation:** it uses future samples, so it can't be used for live feedback.

---

## 3. Average reference

At each moment, subtract the average of all 64 channels from every channel.

**Rule:** it removes what most channels share (likely noise) and keeps what's
local to each electrode.

**In my data:** run 6 spikes seen on C3, Cz and C4 got smaller after
re-referencing, which suggests a shared source. The cause wasn't confirmed,
so those trials were flagged and kept.

```
original recording (never changed)
  → filter 1–40 Hz (zero-phase)
  → average reference
  → cut into rest and imagery windows
```

---

## 4. Spectra: FFT and Welch

**FFT:** turns a wiggly line over time into a bar chart of how much energy
there is at each frequency (the spectrum).

- **Bin spacing** = 1 ÷ window length (2 s window → 0.5 Hz; 1 s → 1 Hz).
- **Nyquist** = highest bar = half the sampling rate (160 Hz → 80 Hz).

**Problem:** one FFT is shaky. Each bar is partly luck (noise with true
value 1 gave bars from 0.09 to 1.70).

**Welch:** cut the 2 s window into three 1 s pieces (half overlapping), FFT
each, average the three bar charts. Like weighing yourself 3 times on a
wobbly scale.

| | Single FFT (2 s) | Welch (1 s pieces) |
|---|---|---|
| Bin spacing | 0.5 Hz | 1 Hz |
| Bars in mu (8–13 Hz) | 11 | 6 |
| Shakiness | high | lower |

Coarser bars are fine because mu is 5 Hz wide.

```
filter 1–40 Hz (clean) → average reference → cut windows
  → Welch (bar chart 0–80 Hz) → read the 8–13 Hz bars
```

The filter **cleans**; choosing mu happens at the end.

---

## 5. Band power and counting trials

**Band power:** add up (area under) the mu bars, 8–13 Hz, to get one number
per window. Code: `band_power` uses `trapezoid` (end bars count half).
Each trial gives a rest number and an imagery number, i.e. one vote:
**lower** or **higher**.

**Why count votes instead of trusting one trial or the average:**

1. One trial can go either way by luck. With no real effect, expect about
   half lower (~12 of 24).
2. One extreme trial can flip the average, but it's only one vote in the
   count (P98's mean was pulled by a single −14.3 dB trial).

| Example changes | +1, +2, +1, +1, −2, −15 |
|---|---|
| Count | 2 of 6 lower → mostly higher |
| Average | −2 → looks lower (driven by the −15) |

**My data (P1, Milestone 3):** mu lower in 8/24 trials. Leans toward higher
(ERS), not ERD, but not clearly beyond chance for one person.

---

## 6. Decibels: average ratios first, dB last

**Ratio, not difference:** imagery ÷ rest, so people with bigger overall
power aren't exaggerated.

**dB = 10 × log10(ratio)** makes up and down even:

| ratio | 10 | 2 | 1 | 0.5 | 0.1 |
|---|---|---|---|---|---|
| dB | +10 | +3 | 0 | −3 | −10 |

0 dB = no change; positive = higher (ERS); negative = lower (ERD).

**Order matters.** Test: rest vs itself (right answer 0 dB), slice ratios
0.5, 1.0, 1.5.
- Ratios first: average 1.0 → **0 dB** (correct).
- dB first: −3.0, 0, +1.8 → average **−0.4 dB** (fake drop).

dB stretches dips and squashes bumps, so averaging dB values is pulled
downward by noise. **Rule:** average plain numbers, convert to dB once at
the end.

**My data:** Milestone 4 dB-first map showed blue in rest (method bias);
ratios-first gave −0.09 dB for rest vs itself (≈ 0).

---

## 7. Time–frequency maps and the window-length trade-off

**Building the map:**
1. Cut a 1 s chunk (160 samples, Hann), compute its spectrum.
2. Turn the bar chart on its side and swap bar height for colour: that is
   **one column**.
3. Slide 0.1 s, repeat. Line the columns up: x = time (chunk **centre**),
   y = frequency, colour = power.
4. Divide by the rest level, average ratios across trials, dB last (§6).

**A column is not one moment.** It blends everything in
**centre ± half the window**. A column centred at +1.5 s with a 1 s window
covers 1.0 to 2.0 s.

**Which slices count:** only chunks fully inside a window.
- Rest −2 to 0 s: centres −1.5 to −0.5 → **11** slices.
- Imagery 1 to 3 s: centres 1.5 to 2.5 → **11** slices.
- Count = gaps + 1, because both ends are included (1.0 ÷ 0.1 = 10 gaps).

**Smearing:** a short burst at −0.3 s appears in every column whose chunk
reaches it.

| Window | Half | Columns containing it | Leaks past cue? | Mu rows |
|---|---|---|---|---|
| 1 s | 0.5 s | −0.8 to +0.2 | yes | 6 (1 Hz) |
| 0.5 s | 0.25 s | −0.55 to −0.05 | no | 3 (2 Hz) |

**Trade-off:** long window = fine frequency rows, blurry timing. Short
window = sharp timing, coarse rows (1 / window).

**Step size** only sets how many columns are drawn. With a 0.1 s step,
neighbouring 1 s chunks share 90% of their samples, so the map looks
smooth but timing is still blurred over 1 s. Only a shorter window
sharpens timing.

**My data:** kept 1 s because mu is 5 Hz wide and needs 1 Hz rows. The
reddening near −0.5 s may be one burst smeared across columns (observation
only). Anything within ~0.5 s of the cue can bleed across it.

---

## 8. Freezing settings and quality rules before seeing new data

**The problem:** many reasonable choices. 3 electrodes × 2 bands × 3
imagery windows = **18** versions of the analysis. With no real effect and
a 5% fluke rate each, 18 × 0.05 ≈ **1 fluke expected**, and about a **60%**
chance at least one looks "clearly significant" (1 − 0.95¹⁸ ≈ 0.6).
Try everything and report the best → the data picked the answer.

**The fix:** explore, then freeze, then confirm.

```
EXPLORE (P1, Milestones 1–4) ──FREEZE──► CONFIRM (5 new people, Milestone 5)
```

P1 helped choose the settings, so P1 can't test them. The new people can.

**What I froze (November 1, before viewing new data):**
- Settings (`config.py`): Cz, mu 8–13 Hz, rest −2 to 0 s, imagery 1 to 3 s,
  1–40 Hz filter, 1 s window.
- Who: random draw, seed 2026 (1, 33, 14, 79, 98). Replace only for
  data-format problems, never for how results look.
- Quality: flag if Cz > 150 µV peak-to-peak; flag = check, not delete;
  main analysis keeps all trials; sensitivity check without flags; nobody
  dropped for many flags. Relative rule (3 × median) as a cross-check.

**The sealed envelope:**
1. **Recipe:** run the frozen settings and rules exactly as written.
2. **Main result:** whatever the recipe gives is the headline, even if mixed.
3. **Extras:** allowed, but labelled "decided after seeing results" and
   treated as ideas to test, not proof.

**Test for any change:**
- Decided before seeing results, or for a reason unrelated to them
  (e.g. a missing file)? → OK.
- Decided after, but it *adds* a labelled check rather than *changing* the
  main result? → OK.
- Otherwise → Not OK, even if the reason sounds sensible.

| Example | Verdict | Why |
|---|---|---|
| Also report C3 / beta, labelled exploratory | OK | Main result unchanged |
| Switch main result to C3 because it looks cleaner | Not OK | Data picked the recipe |
| Replace P33 for missing run 10, before looking | OK | Frozen format rule |
| Replace P33 because result is mixed | Not OK | Reason is the result |
| Drop P98's −14.3 dB trial from main result | Not OK | Changes main result after seeing it |

**My data:** P79 had 5 flags (151–172 µV, median 120 µV). Raising the
threshold to 200 µV would have un-flagged all 5. A sensible reason, but
chosen after seeing the result, so not allowed. Instead: kept 150 µV,
noted "likely overall amplitude", the pre-planned relative rule flagged
none, and the sensitivity check showed P79 stays "higher" (6/24 → 5/19
lower).

---

## 9. Bootstrap: within one person vs across people

**The question:** P1's mean is +0.94 dB from 24 trials. If P1 were recorded
again, how far could that mean move just by luck? The bootstrap fakes a
re-recording from the trials I already have.

**How (tiny example, 5 trials: +1, +2, −1, +3, 0 → mean +1.0):**
1. Draw 5 trials **with replacement** (repeats allowed, some left out):
   `+2 +2 −1 0 +3` → +1.2; `−1 −1 0 +1 +2` → +0.2. Without replacement
   every set would be identical.
2. Repeat 10,000 times (`N_BOOT = 10_000`, seed 2026) → 10,000 means.
3. Sort, cut the lowest 250 and highest 250 → the middle 9,500 = **95%
   interval**.

**Reading it:** whole interval on one side of 0 → reliable direction.

| Person | Mean (dB) | 95% interval | Verdict |
|---|---|---|---|
| P1 | +0.94 | [+0.20, +1.66] | reliably higher |
| P33 | −0.40 | [−1.75, +0.86] | unclear |
| P14 | −2.68 | [−4.14, −1.07] | reliably lower |
| P79 | +1.54 | [+0.50, +2.59] | reliably higher |
| P98 | −3.23 | [−5.35, −1.02] | lower, borderline (count crosses 50%) |

**Resample whole trials, never time slices.** Slices in one trial overlap
90% (§7), so they are not independent; using them would make the interval
falsely narrow.

**Two different questions, two different bootstraps:**

| | Within one person | Across people |
|---|---|---|
| Asks | Is *this* person's change reliable? | Is there a direction shared by people in general? |
| Luck comes from | which trials I got | which people I picked |
| Resample | trials | people (one number each) |

**Across people (my data):** person means +0.94, −0.40, −2.68, +1.54,
−3.23 → average **−0.77 dB [−2.44, +0.91]**, crosses 0.
- Pretend group `P98 P14 P14 P33 P98` → −2.44 = the low end: a group of only
  strong-lowering people. Packed with P79/P1 → the high end.
- Only 5 people who disagree → pretend groups swing a lot → wide, rough
  interval.

**"Group crosses 0" ≠ "mu didn't change".** 4 of 5 individually exclude 0,
but in opposite directions (P1, P79 higher; P14, P98 lower), so the average
cancels. Correct reading: **people don't agree on the direction.**

---

## 10. What the result can and can't claim

**The question:** which sentences about my numbers could I defend if someone
asked "how do you know?"

**Three filters for every sentence:**

| Filter | Asks | My answer |
|---|---|---|
| Who? | These people, or people in general? | 5 randomly chosen people out of 109 |
| What/where? | Under exactly which settings? | Cz, mu 8–13 Hz, imagery 1–3 s vs rest −2–0 s, frozen settings |
| Why? | Did imagery *cause* it? | I compared two windows; I never tested the cause |

**CAN claim:**
- 4 of 5 people show a reliable change (interval excludes 0), in
  **opposite directions**: P1, P79 higher; P14 lower; P98 lower (borderline);
  P33 unclear.
- No consistent group direction: −0.77 dB [−2.44, +0.91]. The interval
  crosses 0 because the directions cancel, not because nothing changed.
- Removing flagged trials changed nobody's direction.
- Settings and participants were fixed before I saw the data.

**CAN'T claim:**

| Tempting sentence | Problem | Filter |
|---|---|---|
| "Motor imagery produces mu ERD" | Only 2/5 reliably lower; 2 went up | Who |
| "Mu doesn't change during imagery" | Crossing 0 ≠ no change | Who |
| "P1/P79 didn't really imagine" / "use a different strategy" | Never measured | Why |
| "Holds over motor cortex" | Cz only (feet area); hand imagery is usually C3/C4 | What/where |
| "Imagery caused it" | Visual cue and anticipation are possible causes; no cue-only control | Why |
| "Could drive a BCI" | Zero-phase filtering is offline only; single trials are noisy (P1 lower in 7/24) | What/where |
| "Useful for rehab" | Healthy people; no clinical outcome measured | Why |

**Trap I fell into:** "reliable change" ≠ "reliable decrease".
- Reliable change (either direction) = **4**.
- Reliably lower = **2** (P14, and P98 borderline).
- "3 of 5 lower on average" is true but says nothing about reliability.

**Honest one-liner:**
> 2 of 5 participants showed reliably lower mu power during imagery (P14,
> and P98 borderline), 2 showed reliably higher (P1, P79), and 1 was unclear
> (P33), so there was no consistent group direction.

P98 wording: mean reliably lower (−3.23 dB [−5.35, −1.02]), but the share
of lower trials (67%) was not clearly above half.
