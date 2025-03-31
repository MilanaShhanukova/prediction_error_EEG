import mne
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from mne.viz import plot_compare_evokeds
from mne_bids import BIDSPath

# Define roots and constants
bids_root = Path("./ds003846-2.0.2")
deriv_root = Path("./bids_derivatives")
TASK = "PredictionError"
EVENT_ID = {"normal": 2, "conflict": 3}
TMIN, TMAX = -0.3, 0.7

# Define subjects and sessions as lists
subjects = ["02", "06", "07", "08", "11", "13", "16"]
sessions = ["EMS", "Vibro", "Visual"]

group_evokeds = {}

# Iterate over defined subjects and sessions
for sub in subjects:
    for ses in sessions:
        # Build the BIDSPath for the cleaned raw file in the derivatives folder
        bids_deriv = BIDSPath(
            root=deriv_root,
            subject=sub,
            session=ses,
            task=TASK,
            datatype="eeg",
            suffix="raw",         # legacy suffix
            processing="clean",   # processing label (will add proc-clean)
            extension=".fif",
            check=False,          # bypass strict naming rules
        )
        if not bids_deriv.fpath.exists():
            print(f"Skipping sub-{sub}, ses-{ses}: {bids_deriv.fpath.name} not found.")
            continue

        print(f"Loading cleaned raw for sub-{sub}, ses-{ses}")
        raw = mne.io.read_raw_fif(bids_deriv.fpath, preload=True)
        # raw.filter(l_freq=None, h_freq=35)

        # Build the BIDSPath for the events file in the original BIDS dataset
        bids_events = BIDSPath(
            root=bids_root,
            subject=sub,
            session=ses,
            task=TASK,
            datatype="eeg",
            suffix="events",
            extension=".tsv",
        )
        if not bids_events.fpath.exists():
            print(f"Events file not found for sub-{sub}, ses-{ses}")
            continue

        events_df = pd.read_csv(bids_events.fpath, sep="\t")
        events = []
        for _, row in events_df.iterrows():
            # Parse the "value" field into a dictionary
            parts = dict(item.split(":") for item in row["value"].split(";"))
            if parts.get("box") == "touched":
                sample = int(round(float(row["onset"]) * raw.info["sfreq"]))
                events.append([sample, 0, EVENT_ID[parts["normal_or_conflict"]]])
        events = np.array(events, int)

        epochs = mne.Epochs(
            raw,
            events,
            event_id=EVENT_ID,
            tmin=TMIN,
            tmax=TMAX,
            baseline=(None, 0),
            preload=True,
            event_repeated="drop",
        )
        # Drop noisy epochs
        peak_to_peak = np.ptp(epochs.get_data(), axis=2).mean(axis=1)
        threshold = np.percentile(peak_to_peak, 80)
        noisy_epochs = peak_to_peak > threshold
        epochs.drop(indices=np.where(noisy_epochs)[0], reason="manual")

        # Pick channel FCz only
        epochs_normal = epochs["normal"].pick_channels(["FCz"])
        epochs_conflict = epochs["conflict"].pick_channels(["FCz"])

        # Use session as the key for grouping evoked responses
        group_evokeds.setdefault(ses, {"normal": [], "conflict": []})
        group_evokeds[ses]["normal"].append(epochs_normal)
        group_evokeds[ses]["conflict"].append(epochs_conflict)

# Compute grand averages for each session
grand_averages = {}
for session, conds in group_evokeds.items():
    all_norm = mne.concatenate_epochs(conds["normal"]).average().filter(l_freq=None, h_freq=10)
    all_conf = mne.concatenate_epochs(conds["conflict"]).average().filter(l_freq=None, h_freq=10)
    diff = mne.combine_evoked([all_conf, all_norm], weights=[1, -1])
    grand_averages[session] = {"normal": all_norm, "conflict": all_conf, "difference": diff}

# Plot
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
# Use the channel name from one of the evoked objects (FCz)
channel = next(iter(grand_averages.values()))["normal"].info["ch_names"][0]

plot_compare_evokeds(
    {sess: grand_averages[sess]["normal"] for sess in grand_averages},
    picks=channel,
    combine="mean",
    ci=True,
    axes=axes[0],
    title="Normal Trials",
    show=False,
)
plot_compare_evokeds(
    {sess: grand_averages[sess]["conflict"] for sess in grand_averages},
    picks=channel,
    combine="mean",
    ci=True,
    axes=axes[1],
    title="Conflict Trials",
    show=False,
)
plot_compare_evokeds(
    {sess: grand_averages[sess]["difference"] for sess in grand_averages},
    picks=channel,
    combine="mean",
    ci=True,
    axes=axes[2],
    title="Difference (C-N)",
    show=False,
)

# Annotate plots with channel name and voltage range
for ax in axes:
    ymin, ymax = ax.get_ylim()
    ax.text(
        ax.get_xlim()[0] - 0.1,
        ymax,
        f"{channel}\n+{int(ymax)}µV",
        fontsize=10,
        ha="center",
        va="bottom",
        weight="bold",
    )
    ax.text(
        ax.get_xlim()[0] - 0.1,
        ymin,
        f"-{int(abs(ymin))}µV",
        fontsize=10,
        ha="center",
        va="top",
        weight="bold",
    )

plt.tight_layout()
plt.show()
