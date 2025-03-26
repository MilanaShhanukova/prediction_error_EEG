import mne
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from mne.viz import plot_compare_evokeds

# Paths
DERIV_ROOT = Path("./bids_derivatives")
BIDS_ROOT = Path("./ds003846-2.0.2")
TASK = "PredictionError"
EVENT_ID = {"normal": 2, "conflict": 3}
TMIN, TMAX = -0.3, 0.7

# Automatically discover subjects & sessions
group_evokeds = {}
for sub_dir in sorted(DERIV_ROOT.glob("sub-*")):
    subject = sub_dir.name
    for ses_dir in sorted(sub_dir.glob("ses-*")):
        session = ses_dir.name
        eeg_dir = ses_dir / "eeg"
        clean_raw = next(eeg_dir.glob(f"{subject}_{session}_task-{TASK}_proc-clean_raw.fif"), None)
        if clean_raw is None:
            continue

        print(f"Loading cleaned raw for {subject}, {session}")
        raw = mne.io.read_raw_fif(clean_raw, preload=True)
        raw.filter(l_freq=None, h_freq=35)
        # Read BIDS events TSV
        events_file = BIDS_ROOT / subject / session / "eeg" / f"{subject}_{session}_task-{TASK}_events.tsv"
        events_df = pd.read_csv(events_file, sep="\t")
        events = []
        for _, row in events_df.iterrows():
            parts = dict(item.split(":") for item in row["value"].split(";"))
            if parts.get("box") == "touched":
                sample = int(round(float(row["onset"]) * raw.info["sfreq"]))
                events.append([sample, 0, EVENT_ID[parts["normal_or_conflict"]]])
        events = np.array(events, int)

        epochs = mne.Epochs(raw, events, event_id=EVENT_ID, tmin=TMIN, tmax=TMAX,
                            baseline=(None, 0), preload=True, event_repeated="drop")
        # Drop the worst 20% of epochs by peak-to-peak amplitude
        ptp = np.ptp(epochs.get_data(), axis=2).mean(axis=1)
        threshold = np.percentile(ptp, 90)
        epochs.drop(np.where(ptp > threshold)[0], reason="ptp_reject")

        # Pick FCz only
        epochs_normal = epochs["normal"].pick_channels(["FCz"])
        epochs_conflict = epochs["conflict"].pick_channels(["FCz"])

        group_evokeds.setdefault(session, {"normal": [], "conflict": []})
        group_evokeds[session]["normal"].append(epochs_normal)
        group_evokeds[session]["conflict"].append(epochs_conflict)

# Compute grand averages
grand_averages = {}
for session, conds in group_evokeds.items():
    all_norm = mne.concatenate_epochs(conds["normal"]).average().filter(l_freq=None, h_freq=10)
    all_conf = mne.concatenate_epochs(conds["conflict"]).average().filter(l_freq=None, h_freq=10)
    grand_averages[session] = {"normal": all_norm, "conflict": all_conf,
                                "difference": mne.combine_evoked([all_conf, all_norm], weights=[1, -1])}

# Plot
fig, axes = plt.subplots(1, len(grand_averages), figsize=(15, 5), sharey=True)
channel = next(iter(grand_averages.values()))["normal"].info["ch_names"][0]

plot_compare_evokeds({sess: grand_averages[sess]["normal"] for sess in grand_averages}, picks=channel,
                     combine="mean", ci=True, axes=axes[0], title="Normal Trials", show=False)
plot_compare_evokeds({sess: grand_averages[sess]["conflict"] for sess in grand_averages}, picks=channel,
                     combine="mean", ci=True, axes=axes[1], title="Conflict Trials", show=False)
plot_compare_evokeds({sess: grand_averages[sess]["difference"] for sess in grand_averages}, picks=channel,
                     combine="mean", ci=True, axes=axes[2], title="Difference (C-N)", show=False)

for ax in axes:
    ymin, ymax = ax.get_ylim()
    ax.text(ax.get_xlim()[0] - 0.1, ymax, f"{channel}\n+{int(ymax)}µV", fontsize=10, ha="center", va="bottom", weight="bold")
    ax.text(ax.get_xlim()[0] - 0.1, ymin, f"-{int(abs(ymin))}µV", fontsize=10, ha="center", va="top", weight="bold")
plt.tight_layout()
plt.show()
