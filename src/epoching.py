import pandas as pd
import numpy as np
import mne


def create_events(events_file, event_id, sfreq):
    events_df = pd.read_csv(events_file, sep="\t")

    events = [] 
    print(f"Sampling frequency: {sfreq} Hz")

    for _, row in events_df.iterrows():
        event_dict = dict(item.split(":") for item in row["value"].split(";"))

        if "box" in event_dict and event_dict["box"] == "touched":
            sample_index = int(round(float(row["onset"]) * sfreq)) 
            event_type = event_id[event_dict["normal_or_conflict"]]

            events.append([sample_index, 0, event_type])

    events = np.array(events)

    return events


def create_epochs(ica_sessions, data_paths, subject, tmin=-0.3, tmax=0.7):
    """
    Creates stimulus-aligned epochs from ICA-processed EEG sessions.

    Parameters
    ----------
    ica_sessions : dict
        Dictionary with session names as keys and mne.io.Raw objects as values.
    data_paths : dict
        Dictionary mapping session names to file paths containing event files.
    subject : str
        Subject identifier for constructing event file names.
    tmin : float, optional
        Start time (in seconds) before the event. Default is -0.3s.
    tmax : float, optional
        End time (in seconds) after the event. Default is 0.7s.

    Returns
    -------
    epochs_sessions : dict
        Dictionary with session names as keys and MNE Epochs objects as values.
    """

    event_id = {"normal": 2, "conflict": 3}  # Define event mapping
    epochs_sessions = {}  # Store epochs per session

    for session, raw in ica_sessions.items():
        print(f"\nCreating stimulus-aligned epochs for {session}...")

        # find and separate necessary events
        events_file = data_paths[session] / f"{subject}_{session}_task-PredictionError_events.tsv"
        events = create_events(events_file, event_id, sfreq=raw.info["sfreq"])

        # create epochs, dropping duplicate events
        epochs = mne.Epochs(
            raw, events, event_id=event_id, tmin=tmin, tmax=tmax,
            baseline=(None, 0), preload=True, event_repeated="drop"
        )
        peak_to_peak = np.ptp(epochs.get_data(), axis=2).mean(axis=1)

        threshold = np.percentile(peak_to_peak, 80)
        noisy_epochs = peak_to_peak > threshold

        # drop the noisiest epochs
        epochs.drop(indices=np.where(noisy_epochs)[0], reason='manual')

        epochs_sessions[session] = epochs
        print(f"  Extracted {len(epochs)} epochs for {session}.")

    return epochs_sessions


