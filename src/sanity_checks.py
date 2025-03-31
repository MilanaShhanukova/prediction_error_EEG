import mne
import matplotlib.pyplot as plt


def plot_psd_sanity(raw, session):
    """
    Plot the Power Spectral Density (PSD) for the given Raw object.

    Parameters
    ----------
    raw : mne.io.Raw
        Preprocessed Raw object.
    session : str
        Name of the session.
    """
    print(f"Plotting PSD for sanity check of {session}...")
    raw.plot_psd(fmin=0.5, fmax=125, average=True, show=True)


def check_channel_statistics(raw, session):
    """
    Compute and print basic channel statistics (mean and standard deviation).

    Parameters
    ----------
    raw : mne.io.Raw
        Preprocessed Raw object.
    session : str
        Name of the session.
    """
    data = raw.get_data()
    mean_vals = data.mean(axis=1)
    std_vals = data.std(axis=1)
    print(f"\nChannel statistics for {session}:")
    for ch, mean, std in zip(raw.ch_names, mean_vals, std_vals):
        print(f"  {ch}: mean = {mean:.10f}, std = {std:.10f}")
