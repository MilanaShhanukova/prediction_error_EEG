# ─── PATHS ──────────────────────────────────────────────────────────────────────
bids_root      = "./ds003846-2.0.2"      # original raw BIDS (for provenance only)
deriv_root     = "./bids_derivatives"    # where your cleaned *.fif lives
use_derivatives = True                  # ← critical: read derivatives as “raw” input

# ─── SUBJECTS & SESSIONS ───────────────────────────────────────────────────────
subjects       = ["02", "06"]
sessions       = ["EMS", "Vibro", "Visual"]

# ─── EEG PREPROCESSING ─────────────────────────────────────────────────────────
ch_types              = ["eeg"]
data_type             = 'eeg'
eeg_template_montage  = "standard_1020"
l_freq                = 1.0
h_freq                = 124.9
raw_resample_sfreq    = 250
eeg_reference         = "average"
notch_freq            = [50]


# For reproducibility in ICA and other steps
random_state          = 42

# ─── ICA ───────────────────────────────────────────────────────────────────────
spatial_filter        = "ica"
ica_algorithm         = "extended_infomax"
ica_n_components      = 20
reject                = None

# ─── EPOCHING ───────────────────────────────────────────────────────────────────
# We dont actually use the epoch data but the pipeline needs it for the ica fitting
task                  = "PredictionError"
task_is_rest          = True
epochs_tmin           = 0.0
epochs_tmax           = 10.0
rest_epochs_overlap   = 0.0
rest_epochs_duration  = 10.0
baseline              = None

# ─── PARALLELIZATION ───────────────────────────────────────────────────────────
n_jobs               = 4
parallel_backend     = "loky"