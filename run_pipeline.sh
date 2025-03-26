#!/bin/bash

# ----------------------------------------
# 1. Patch BIDS metadata
# ----------------------------------------
# Some *_scans.tsv files contain very old acquisition times that cause
# the BIDS pipeline to complain. We manually update these times to a more
# recent date so the pipeline can run without errors.
echo "Fixing acq_time in _scans.tsv files..."
python3 -u patch_acq_time.py

# ----------------------------------------
# 2. Prepare the raw EEG files
# ----------------------------------------
# We add an FCz reference channel and remove the "BrainVision RDA_" prefix from
# channel names so that the BIDS pipeline can properly set the standard_1020
# montage. We coudlnt add new reference channels or rename existing channels
# directly within the BIDS pipeline, so we do it here instead.
# limitations around channel naming and referencing.
echo "Preparing and standardizing raw EEG files for bids pipeline...ex"
python3 -u prepare_raw.py

# ----------------------------------------
# 3. Run the core pipeline (up to ICA fitting)
# ----------------------------------------
# Here we invoke the MNE-BIDS-Pipeline steps:
#   - set standard_1020 montage
#   - Apply bandpass and notch filters
#   - Re-reference to average
#   - Fit ICA (without applying it yet)
#
# We stop after the ICA is fitted, because we plan to apply ICLabel
# and exclude components ourselves on the raw data.
echo "Running MNE-BIDS-Pipeline steps..."
mne_bids_pipeline \
  --config config.py \
  --steps preprocessing/_01_data_quality,preprocessing/_04_frequency_filter,preprocessing/_06a1_fit_ica,preprocessing/_06a2_find_ica_artifacts,preprocessing/_07_make_epochs,preprocessing/_08a_apply_ica

# ----------------------------------------
# 4. Apply ICLabel and exclude unwanted ICs
# ----------------------------------------
# We rely on ICLabel to classify each ICA component and then we remove
# components not labeled as "brain" or "other". We do this on the
# raw data.
# echo "Applying ICLabel and removing non-brain components..."
# python3 -u apply_iclabel.py

# ----------------------------------------
# 5. Group-level analysis
# ----------------------------------------
# In this step, we loop over each subject and session to:
#   1) Read the cleaned raw data.
#   2) Parse the events from a BIDS TSV file to identify “touched” trials,
#      classifying them as either “normal” or “conflict.”
#   3) Epoch the data from –0.3 to 0.7 s, apply baseline correction, and
#      discard the 20% of epochs with the largest peak-to-peak amplitude.
#   4) Focus on the FCz channel by picking only "FCz."
#   5) Aggregate all “normal” and “conflict” epochs across subjects/sessions,
#      then compute their grand-average ERPs. We also create a "difference"
#      waveform by subtracting normal from conflict.
#   6) Finally, we plot the grand averages for “normal,” “conflict,” and
#      their difference, all on a single figure for quick comparison.
#
# For more detailes refer to the accompanying notebook which contains additional plots and steps.
python3 -u group_analysis.py
