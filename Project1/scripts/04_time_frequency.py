import sys
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eeg_rehab.config import (
    PARTICIPANT, CHANNELS, PRIMARY_CHANNEL, REST_LABEL, FOOT_LABEL,
    VOLTS_TO_UV, REST_WINDOW, IMAGERY_WINDOW, EPOCH_WINDOW,
)
from eeg_rehab.data import load_runs
from eeg_rehab.trials import get_task_annotations, window_has_condition
from eeg_rehab.preprocessing import preprocess_runs

recordings = load_runs(PARTICIPANT)
_, referenced_runs = preprocess_runs(recordings)

epochs = []
epoch_keys = []

for run_number, recording in referenced_runs.items():
    sfreq = recording.info["sfreq"]
    n_samples = round((EPOCH_WINDOW[1] - EPOCH_WINDOW[0]) * sfreq)
    annotations = get_task_annotations(recording)
    foot_cues = [onset for onset, end, label in annotations
                 if label == FOOT_LABEL]

    for trial_number, cue in enumerate(foot_cues, start=1):
        start_sample = round((cue + EPOCH_WINDOW[0]) * sfreq)
        start = start_sample / sfreq
        stop = (start_sample + n_samples) / sfreq

        # Before the cue must be all rest, after the cue all foot imagery
        rest_ok = window_has_condition(start, cue, REST_LABEL, annotations)
        foot_ok = window_has_condition(cue, stop, FOOT_LABEL, annotations)
        if not (rest_ok and foot_ok):
            print(f"Skipped run {run_number} trial {trial_number}")
            continue

        epoch = recording.get_data(picks=CHANNELS, start=start_sample,
                                   stop=start_sample + n_samples)
        epochs.append(epoch)
        epoch_keys.append((run_number, trial_number))

epochs = np.array(epochs)
print(f"\nStep 1b: epochs shape {epochs.shape} (trials, channels, samples)")
print(f"First: run {epoch_keys[0][0]} trial {epoch_keys[0][1]}, "
      f"last: run {epoch_keys[-1][0]} trial {epoch_keys[-1][1]}")


times = np.arange(epochs.shape[2]) / sfreq + EPOCH_WINDOW[0]
print(f"Time axis: {times[0]:.3f} to {times[-1]:.3f} s relative to cue")

ch = CHANNELS.index(PRIMARY_CHANNEL)
run, trial = epoch_keys[0]

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(times, epochs[0, ch] * VOLTS_TO_UV, color="black", lw=1)
ax.axvline(0, color="red", lw=1.5, label="Cue (time 0)")
ax.axvspan(*REST_WINDOW, color="tab:blue", alpha=0.15, label="Rest window")
ax.axvspan(*IMAGERY_WINDOW, color="tab:orange", alpha=0.15,
           label="Imagery window")
ax.set_xlim(times[0], times[-1])
ax.set_xlabel("Time relative to cue (s)")
ax.set_ylabel("Cz (µV)")
ax.set_title(f"Participant {PARTICIPANT}, run {run} trial {trial}: "
             f"cue-aligned epoch")
ax.legend(loc="upper right")
fig.tight_layout()
plt.show(block=False)

# Keep all figures open until closed
plt.show()