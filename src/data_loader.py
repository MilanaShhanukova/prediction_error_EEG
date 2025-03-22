import mne
from pathlib import Path

def load_raw_sessions(base_path, subject):
    """
    Load raw EEG sessions for the subject.

    For each session (EMS, Visual, Vibro):
      - Load the BrainVision .vhdr file.
      - Add 'FCz' as a reference channel.
      - Clean channel names by removing the "BrainVision RDA_" prefix.
      - Set the standard 10-20 montage.

    Parameters
    ----------
    base_path : Path
        Base directory containing the dataset.
    subject : str
        Subject identifier (e.g., "sub-02").

    Returns
    -------
    raw_sessions : dict
        Dictionary with session names as keys and mne.io.Raw objects as values.
    """
    sessions = ["ses-EMS", "ses-Visual", "ses-Vibro"]
    raw_sessions = {}
    for session in sessions:
        path = base_path / subject / session / "eeg"
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        vhdr_file = path / f"{subject}_{session}_task-PredictionError_eeg.vhdr"
        if not vhdr_file.exists():
            raise FileNotFoundError(f"File not found: {vhdr_file}")
        print(f"Loading data for {session} from {vhdr_file}...")
        raw = mne.io.read_raw_brainvision(str(vhdr_file), preload=True)
        raw = mne.add_reference_channels(raw, ref_channels=["FCz"])
        raw.rename_channels(lambda x: x.replace("BrainVision RDA_", ""))
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage)
        raw_sessions[session] = raw
    return raw_sessions
