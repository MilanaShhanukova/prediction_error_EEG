import numpy as np
import pandas as pd
import mne
from mne import io, viz
import matplotlib.pyplot as plt


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


def process_subject_epochs(subjects, sessions, base_path, processed_base_path, event_id, tmin=-0.3, tmax=0.7):
    """
    Processes EEG data for multiple subjects and sessions, extracting and filtering epochs.
    
    Parameters:
    - subjects (list): List of subject identifiers.
    - sessions (list): List of session identifiers.
    - base_path (Path): Base directory containing the EEG data.
    - event_id (dict): Mapping of condition labels to event IDs.
    - tmin (float): Start time before event onset (in seconds).
    - tmax (float): End time after event onset (in seconds).
    
    Returns:
    - group_evokeds (dict): Dictionary containing processed epochs for each session and condition.
    """
    group_evokeds = {session: {"normal": [], "conflict": []} for session in sessions}
    
    for subject in subjects:
        for session in sessions:
            print(f"Processing {subject}, {session}...")
            
            # Load preprocessed raw file
            processed_raw_path = (processed_base_path / subject / f"{session}_processed_raw.fif")
            raw = io.read_raw_fif(processed_raw_path, preload=True)
            
            # Load events file
            events_file = base_path / subject / session / "eeg" / f"{subject}_{session}_task-PredictionError_events.tsv"
            events_df = pd.read_csv(events_file, sep="\t")
            
            # Convert events to sample indices
            events_list = []
            for _, row in events_df.iterrows():
                event_dict = dict(item.split(":") for item in row["value"].split(";"))
                if "box" in event_dict and event_dict["box"] == "touched":
                    onset_in_sec = float(row["onset"])
                    sample_index = int(round(onset_in_sec * raw.info["sfreq"]))
                    cond_label = event_dict["normal_or_conflict"]
                    this_event_id = event_id[cond_label]
                    events_list.append([sample_index, 0, this_event_id])
            
            events_array = np.array(events_list, int)
            
            # Create epochs
            epochs = mne.Epochs(
                raw, events_array, event_id=event_id, tmin=tmin, tmax=tmax,
                baseline=(None, 0), preload=True, event_repeated="drop"
            )
            
            # Drop noisy epochs
            peak_to_peak = np.ptp(epochs.get_data(), axis=2).mean(axis=1)
            threshold = np.percentile(peak_to_peak, 80)
            noisy_epochs = peak_to_peak > threshold
            epochs.drop(indices=np.where(noisy_epochs)[0], reason="manual")
            
            # Pick FCz channel
            epochs_filtered_normal = epochs["normal"].pick_channels(["FCz"])
            epochs_filtered_conflict = epochs["conflict"].pick_channels(["FCz"])
            
            # Append to group dictionary
            group_evokeds[session]["normal"].append(epochs_filtered_normal)
            group_evokeds[session]["conflict"].append(epochs_filtered_conflict)
    
    return group_evokeds


def compute_grand_averages(group_evokeds, sessions):
    grand_averages = {}
    
    for session in sessions:
        all_normal_epochs = mne.concatenate_epochs(group_evokeds[session]["normal"])
        all_conflict_epochs = mne.concatenate_epochs(group_evokeds[session]["conflict"])

        evoked_normal = all_normal_epochs.average().filter(l_freq=None, h_freq=10, verbose=False)
        evoked_conflict = all_conflict_epochs.average().filter(l_freq=None, h_freq=10, verbose=False)
        evoked_difference = mne.combine_evoked([evoked_conflict, evoked_normal], weights=[1, -1])

        grand_averages[session] = {
            "normal": evoked_normal,
            "conflict": evoked_conflict,
            "difference": evoked_difference
        }
    
    return grand_averages


def plot_evoked_comparisons(grand_averages, sessions):
    styles = {
        'ses-EMS': {'color': '#FFD700', 'linestyle': '-'},
        'ses-Vibro': {'color': '#FF6B6B', 'linestyle': '-'},
        'ses-Visual': {'color': '#4169E1', 'linestyle': '-'}
    }
    
    evokeds_normal = {session: grand_averages[session]["normal"] for session in sessions}
    evokeds_conflict = {session: grand_averages[session]["conflict"] for session in sessions}
    evokeds_difference = {session: grand_averages[session]["difference"] for session in sessions}
    
    channel_name = evokeds_normal[sessions[0]].info["ch_names"][0]
    
    fig, axes = plt.subplots(1, 3, figsize=(25, 7))
    for ax_idx, (condition, evokeds) in enumerate(zip(['Normal', 'Conflict', 'Difference'], 
                                                    [evokeds_normal, evokeds_conflict, evokeds_difference])):
        ax = axes[ax_idx]
        viz.plot_compare_evokeds(
            evokeds,
            picks=channel_name,
            combine="mean",
            ci=0.95,
            axes=ax,
            styles=styles,
            show=False,
            show_sensors=False
        )
        ax.set_ylim(-3, 10)
        ax.set_yticks([-1, 0, 2.5, 5, 7.5, 10])
        ax.text(-0.15, 10, 'FCz\n+10µV', ha='right', va='top')
        ax.text(-0.15, -1, '-1µV', ha='right', va='bottom')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
        caption = ["Normal Trials", "Mismatch Trials", "Difference (Mismatch - Match)"][ax_idx]
        ax.text(0.5, -0.2, caption, transform=ax.transAxes, ha='center', va='center',
                fontsize=12, fontweight='bold')
    
    plt.tight_layout(rect=[0, 0.1, 1, 1])
    plt.show()

