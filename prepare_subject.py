import mne
from pathlib import Path
import os
import argparse
from mne_icalabel import label_components
import numpy as np


def load_data(base_path, subject):
    """
    Step 1
    1. Read the data for all sessions,
    2. rename channels,
    3. apply the 10-20 montage.
    """
    data_paths = {
        "ses-EMS": base_path / subject / "ses-EMS" / "eeg",
        "ses-Visual": base_path / subject / "ses-Visual" / "eeg",
        "ses-Vibro": base_path / subject / "ses-Vibro" / "eeg",
    }

    raw_sessions = {}
    for session, path in data_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        vhdr_file = path / f"{subject}_{session}_task-PredictionError_eeg.vhdr"

        if not vhdr_file.exists():
            raise FileNotFoundError(f"File not found: {vhdr_file}")

        print(f"Loading data for {session}...")
        raw = mne.io.read_raw_brainvision(str(vhdr_file), preload=True)
        raw = mne.add_reference_channels(raw, ref_channels=["FCz"])

        print(f"Cleaning channel names for {session}...")
        raw.rename_channels(lambda x: x.replace("BrainVision RDA_", ""))
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage)
        raw_sessions[session] = raw

    return raw_sessions


def filter_downsample(raw_sessions):
    """
    Step 2: Filter the data and downsample it.
    1. Bandpass filter: 1-124.9 Hz
    2. Downsample to 250 Hz
    3. Re-reference to the average.
    4. Notch filtering
    """
    for session, raw in raw_sessions.items():
        print(f"Processing data for {session}...")
        
        # Bandpass filter
        raw.filter(l_freq=1, h_freq=124.9)

        # Downsample
        raw.resample(250)

        # Re-reference
        raw.set_eeg_reference("average")
        raw.notch_filter(freqs=[50])

    return raw_sessions


def ica_analysis(raw_sessions):
    """
    Step 3: Apply ICA to clean artifacts and filter for ERP analysis.
    - ICA is applied with 20 components.
    - Data is filtered between 0.2–35 Hz after ICA.
    """
    ica_sessions = {}
    for session, raw in raw_sessions.items():
        print(f"Running ICA for {session}...")
        ica = mne.preprocessing.ICA(
            n_components=20,
            max_iter="auto",
            method="infomax",
            random_state=97,
            fit_params=dict(extended=True),
        )
        ica.fit(raw)
        ica.apply(raw)

        labels = label_components(raw, ica, method="iclabel")
        ic_labels = labels["labels"]
        ic_probs = labels["y_pred_proba"]

        eye_noise_comps = []
        for comp_idx, (label, prob) in enumerate(zip(ic_labels, ic_probs)):
            if label not in ["brain", "other"] and np.max(prob) > 0.8:
                eye_noise_comps.append(comp_idx)

        print(
            f"Identified {len(eye_noise_comps)} components to remove: {eye_noise_comps}"
        )
        ica.exclude = eye_noise_comps  # Mark components for exclusion
        raw_clean = ica.apply(raw.copy())  # Apply ICA cleaning

        ica_sessions[session] = raw_clean

    for session, raw in ica_sessions.items():
        print(f"Filtering for ERP analysis in {session}...")
        raw.filter(l_freq=None, h_freq=35)

    return ica_sessions


def save_sessions(sessions, save_dir):
    """
    Save processed sessions to disk in FIF format.
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    for session, raw in sessions.items():
        save_path = save_dir / f"{session}_processed_raw.fif"
        print(f"Saving {session} data to {save_path}...")
        raw.save(save_path, overwrite=True)


def main(base_path, save_dir, subject):
    """
    Main function to process EEG data.
    """
    base_path = Path(base_path)
    save_dir = Path(save_dir)

    # Step 1: Create data paths and load raw sessions
    raw_sessions = load_data(base_path, subject)

    # Step 2: Filter and downsample
    filtered_sessions = filter_downsample(raw_sessions)

    # Step 3: Run ICA and ERP-related filtering
    ica_sessions = ica_analysis(filtered_sessions)

    # Save processed sessions
    save_sessions(ica_sessions, save_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process EEG data using MNE.")
    parser.add_argument(
        "--base_path",
        type=str,
        required=True,
        help="Base directory containing the dataset.",
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        required=True,
        help="Directory to save the processed data.",
    )
    parser.add_argument(
        "--subject", type=str, required=True, help="Subject identifier (e.g., sub-02)."
    )

    args = parser.parse_args()
    main(args.base_path, args.save_dir, args.subject)
