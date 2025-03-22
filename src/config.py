# config.py
# Global configuration parameters (mne-bids-style naming)

HIGHPASS = 1.0       # Lower cutoff for bandpass filtering (Hz)
LOWPASS = 124.9      # Upper cutoff for bandpass filtering (Hz)
DOWNSAMPLE = 250     # Target sampling frequency after downsampling (Hz)
NOTCH_FREQS = [50]   # Frequencies for notch filtering (Hz)

ICA_N_COMPONENTS = 20      # Number of ICA components
ICA_RANDOM_STATE = 97      # Random state for reproducibility
