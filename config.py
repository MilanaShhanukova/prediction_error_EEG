# ─── PATHS ──────────────────────────────────────────────────────────────────────
bids_root      = "./ds003846-2.0.2"      # original raw
deriv_root     = "./bids_derivatives"    # processed *.fif files

# ─── SUBJECTS & SESSIONS ───────────────────────────────────────────────────────
subjects       = ["02", "06"]
sessions       = ["EMS", "Vibro", "Visual"]

# ─── EEG PREPROCESSING ─────────────────────────────────────────────────────────
ch_types              = ["eeg"]
data_type             = 'eeg'
eeg_template_montage  = "standard_1020"
# IClabel requirest hfreq <= 100Hz
l_freq                = 1
h_freq                = 100
raw_resample_sfreq    = 200

# find_flat_channels_meg = True
# find_noisy_channels_meg = True
eeg_reference         = "average"
notch_freq            = [50]


# For reproducibility in ICA and other steps
random_state          = 42

# ─── ICA ───────────────────────────────────────────────────────────────────────
spatial_filter        = "ica"
ica_algorithm         = "extended_infomax"
ica_n_components      = 20
ica_use_icalabel      = True
# Only keep brain and other
icalabel_include      = ["brain", "other"]
ica_use_eog_detection = False
ica_use_ecg_detection = False
# reject                = None

# ─── EPOCHING ───────────────────────────────────────────────────────────────────
# We dont actually use the rest epoch data but the pipeline needs it for the ica fitting
task                  = "PredictionError"
task_is_rest          = True
epochs_tmin           = 0.0
epochs_tmax           = 10.0
rest_epochs_overlap   = 0.0
rest_epochs_duration  = 10.0
baseline              = None
reject                = 'autoreject_global'

# ─── PARALLELIZATION ───────────────────────────────────────────────────────────
n_jobs               = 4
parallel_backend     = "loky"

config_validation    = 'warn'