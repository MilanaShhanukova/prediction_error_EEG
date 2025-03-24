import mne

# ─── PATHS ──────────────────────────────────────────────────────────────────────
bids_root      = "./ds003846-2.0.2"      # original raw BIDS (for provenance only)
deriv_root     = "./bids_derivatives"    # where your cleaned *.fif lives
use_derivatives = True                  # ← critical: read derivatives as “raw” input

# ─── SUBJECTS & SESSIONS ───────────────────────────────────────────────────────
subjects       = ["02"]
sessions       = ["EMS", "Vibro", "Visual"]

# ─── EEG PREPROCESSING ─────────────────────────────────────────────────────────
ch_types              = ["eeg"]
montage               = mne.channels.make_standard_montage("standard_1020")
l_freq                = 1.0
h_freq                = 124.9
raw_resample_sfreq    = 250
eeg_reference         = "average"
notch_freq            = [50]

# ─── EPOCHING ───────────────────────────────────────────────────────────────────
task                  = "PredictionError"
task_is_rest          = True
epochs_tmin           = 0.0
epochs_tmax           = 10.0
rest_epochs_overlap   = 0.0
rest_epochs_duration  = 10.0
baseline              = None

# ─── ICA ───────────────────────────────────────────────────────────────────────
spatial_filter        = "ica"
ica_algorithm         = "extended_infomax"
ica_n_components      = 20
reject                = None
