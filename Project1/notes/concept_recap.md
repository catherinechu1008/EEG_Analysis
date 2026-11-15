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
