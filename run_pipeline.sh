#!/bin/bash

# ----------------------------------------
# 1. Patch BIDS metadata
# ----------------------------------------
# Some _scans.tsv files contain very old acquisition times and the pipeline complains
# We update them manually to a more recent time
echo "Fixing acq_time in _scans.tsv files..."
python3 patch_acq_time.py

# ----------------------------------------
# 2. Prepare raw EEG files
# ----------------------------------------
# Standardize raw EEG: add FCz, rename channels, apply montage.
# Workaround for BIDS pipeline limitations with channel naming and referencing.
echo "Preparing and standardizing raw EEG files for pipeline input..."
python3 -u prepare_raw_for_bids_pipeline.py

# ----------------------------------------
# 3. Run core pipeline (preprocessing → ICA fitting)
# ----------------------------------------
# This runs the MNE-BIDS-Pipeline steps:
# - Assess data quality
# - Apply bandpass and notch filters
# - Fit ICA (but do not yet apply it)
echo "Running MNE-BIDS-Pipeline steps..."
mne_bids_pipeline \
  --config config.py \
  --steps preprocessing/_01_data_quality,preprocessing/_04_frequency_filter,preprocessing/_06a1_fit_ica
