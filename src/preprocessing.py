import mne
from config import HIGHPASS, LOWPASS, DOWNSAMPLE, NOTCH_FREQS

def preprocess_raw_sessions(raw_sessions):
    """
    Preprocess each Raw session by:
      1. Bandpass filtering from HIGHPASS Hz to LOWPASS Hz.
      2. Downsampling to DOWNSAMPLE Hz.
      3. Re-referencing to the average.
      4. Notch filtering at frequencies specified in NOTCH_FREQS.

    Parameters
    ----------
    raw_sessions : dict
        Dictionary with session names as keys and mne.io.Raw objects as values.

    Returns
    -------
    raw_sessions : dict
        Preprocessed Raw sessions.
    """
    for session, raw in raw_sessions.items():
        print(f"\n--- Preprocessing {session} ---")
        print(f"  Filtering {HIGHPASS}–{LOWPASS} Hz...")
        raw.filter(l_freq=HIGHPASS, h_freq=LOWPASS)
        print(f"  Downsampling to {DOWNSAMPLE} Hz...")
        raw.resample(DOWNSAMPLE)
        print("  Re-referencing to average...")
        raw.set_eeg_reference("average")
        print(f"  Applying notch filter at {NOTCH_FREQS} Hz...")
        raw.notch_filter(freqs=NOTCH_FREQS)
        print(f"  {session} info: {len(raw.ch_names)} channels, sampling rate: {raw.info['sfreq']} Hz")
    return raw_sessions
