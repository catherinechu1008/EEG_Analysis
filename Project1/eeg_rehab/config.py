"""Analysis settings shared by every script.

Change values here, not inside scripts, so every analysis uses the same
choices. Before Milestone 5, freeze the primary channel, band and window.
"""

from pathlib import Path

# Dataset: PhysioNet EEG Motor Movement/Imagery, runs with T2 = imagined feet
PARTICIPANT = 1
RUNS = [6, 10, 14]

# Annotation labels for runs 6, 10 and 14
REST_LABEL = "T0"
HAND_LABEL = "T1"
FOOT_LABEL = "T2"
TASK_LABELS = [REST_LABEL, HAND_LABEL, FOOT_LABEL]

# Channels (EDF names keep the trailing dots)
CHANNELS = ["C3..", "Cz..", "C4.."]
CHANNEL_LABELS = ["C3", "Cz", "C4"]
PRIMARY_CHANNEL = "Cz.."

# Preprocessing: offline zero-phase FIR band-pass, then average reference
L_FREQ = 1
H_FREQ = 40

# Trial windows in seconds relative to the foot-imagery cue
REST_WINDOW = (-2, 0)
IMAGERY_WINDOW = (1, 3)
EPOCH_WINDOW = (-2, 4)

# Research-based starting ranges, not findings from this participant
MU_BAND = (8, 13)
BETA_BAND = (13, 30)

# MNE stores EEG in volts; plots display microvolts
VOLTS_TO_UV = 1_000_000

# Paths are absolute so scripts work from any working directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
QUALITY_REVIEW_CSV = DATA_DIR / "quality_review.csv"
TRIAL_TABLE_CSV = OUTPUT_DIR / "trial_table.csv"
