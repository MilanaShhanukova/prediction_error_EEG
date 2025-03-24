#!/usr/bin/env python

import argparse
import os
from pathlib import Path

import mne
import numpy as np
from mne_icalabel import label_components


def load_raw_sessions(base_path, subject):
    """
    1) For each of the three sessions (EMS, Visual, Vibro):
       - Load the BrainVision .vhdr file
       - Add 'FCz' as a reference channel
       - Strip 'BrainVision RDA_' prefix from channel names
       - Set the 10-20 montage
    2) Return a dict of {session_name: Raw}.
    """
    data_paths = {
        "ses-EMS": base_path / subject / "ses-EMS" / "eeg",
        "ses-Visual": base_path / subject / "ses-Visual" / "eeg",
        "ses-Vibro": base_path / subject / "ses-Vibro" / "eeg",
    }

    raw_sessions = {}
    for session, path in data_paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        vhdr_file = path / f"{subject}_{session}_task-PredictionError_eeg.vhdr"
        if not vhdr_file.exists():
            raise FileNotFoundError(f"File not found: {vhdr_file}")

        print(f"Loading data for {session} from {vhdr_file}...")
        raw = mne.io.read_raw_brainvision(str(vhdr_file), preload=True)

        # Add FCz reference channel
        raw = mne.add_reference_channels(raw, ref_channels=["FCz"])

        # Clean channel names and set standard montage
        raw.rename_channels(lambda x: x.replace("BrainVision RDA_", ""))
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage)

        raw_sessions[session] = raw

    return raw_sessions


def preprocess_raw_sessions(raw_sessions):
    """
    1) Bandpass filter each Raw to 1-124.9 Hz
    2) Downsample to 250 Hz
    3) Re-reference to the average
    4) Notch filter at 50 Hz
    """
    for session, raw in raw_sessions.items():
        print(f"\n--- Preprocessing {session} ---")

        # 1) Bandpass (1–125 Hz)
        print("  Filtering 1–125 Hz...")
        raw.filter(l_freq=1, h_freq=124.9)

        # 2) Downsample to 250 Hz
        print("  Downsampling to 250 Hz...")
        raw.resample(250)

        # 3) Average reference (including newly added 'FCz')
        print("  Re-referencing to average...")
        raw.set_eeg_reference("average")

        # 4) Notch filter at 50 Hz (plus harmonics if needed)
        print("  Applying notch filter at 50 Hz...")
        raw.notch_filter(freqs=[50])

        # Plot PSD
        # raw.plot_psd(fmin=0.5, fmax=50, average=True)

    return raw_sessions


def run_ica_label_exclude(raw_sessions):
    """
    1) Run ICA (Infomax, n=20, extended=True).
    2) Label components with mne_icalabel.
    3) Exclude components whose labels are not in ["brain", "other"].
    4) Apply ICA to each session's Raw and return a dict of cleaned Raw.
    """
    ica_cleaned = {}

    for session, raw in raw_sessions.items():
        print(f"\n=== ICA for {session} ===")

        # Setup ICA
        ica = mne.preprocessing.ICA(
            n_components=20,
            max_iter="auto",
            method="infomax",
            random_state=97,
            fit_params=dict(extended=True),
        )

        # Fit ICA
        print("  Fitting ICA...")
        ica.fit(raw)

        # ica.plot_components(title=f"ICA Components: {session}")
        # ica.plot_properties(raw, picks=[0, 1, 2])
        # ica.plot_sources(raw, show_scrollbars=False, show=True)

        # Label the ICA components
        print("  Labeling ICA components with ICLabel...")
        ic_labels = label_components(raw, ica, method="iclabel")
        labels = ic_labels["labels"]
        print(f"  ICLabel assigned: {labels}")

        # Exclude any component not labeled "brain" or "other" (matching the notebook)
        exclude_idx = [
            idx for idx, lab in enumerate(labels) if lab not in ["brain", "other"]
        ]
        print(f"  Excluding components: {exclude_idx}")

        # Make a copy and apply ICA to remove those components
        raw_clean = raw.copy()
        ica.apply(raw_clean, exclude=exclude_idx)


        ica_cleaned[session] = raw_clean

    return ica_cleaned


def main():
    """
    complete pipeline:
    1) Parse arguments
    2) Load raw data for a single subject
    3) Preprocess (filter, downsample, re-reference, notch)
    4) Run ICA, label components, exclude artifacts
    """
    parser = argparse.ArgumentParser(description="EEG Preprocessing up to ICA (MNE).")
    parser.add_argument(
        "--base_path",
        type=str,
        required=True,
        help="Base directory containing the dataset (e.g., ./ds003846-2.0.2).",
    )
    parser.add_argument(
        "--subject",
        type=str,
        required=True,
        help="Subject identifier (e.g., sub-02).",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        required=False,
        default=None,
        help="Optional path to save the final cleaned Raw files.",
    )

    args = parser.parse_args()

    base_path = Path(args.base_path)
    subject = args.subject

    # Use provided outdir or default to 'processed_eeg_data'
    outdir = Path(args.outdir) if args.outdir else Path("./processed_eeg")

    print(f"\n\n>>> Starting pipeline for {subject} <<<")

    # Step 1: Load data
    raw_sessions = load_raw_sessions(base_path, subject)

    # Step 2: Preprocess (filter, downsample, re-ref, notch)
    raw_sessions = preprocess_raw_sessions(raw_sessions)

    # Step 3: ICA and artifact rejection
    clean_sessions = run_ica_label_exclude(raw_sessions)

    # (Optional) Save the final cleaned data to .fif
    if outdir:
        # Create a subject-specific directory within the output folder
        subject_outdir = outdir / subject
        subject_outdir.mkdir(exist_ok=True, parents=True)

        for sess, raw_clean in clean_sessions.items():
            out_path = subject_outdir / f"{sess}_cleaned_raw.fif"
            print(f"Saving cleaned {sess} data to {out_path}")
            raw_clean.save(out_path, overwrite=True)


    print("\n>>> Done! <<<\n")


if __name__ == "__main__":
    main()
