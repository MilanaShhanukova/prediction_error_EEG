from pathlib import Path
import mne
from mne_bids import BIDSPath

# === CONFIG ===
bids_root = Path("./ds003846-2.0.2")
subjects  = ["02"]
sessions  = ["EMS", "Vibro", "Visual"]
task      = "PredictionError"

montage = mne.channels.make_standard_montage("standard_1020")

# === PROCESS ===
for sub in subjects:
    for ses in sessions:
        bids_path = BIDSPath(
            root=bids_root,
            subject=sub,
            session=ses,
            task=task,
            datatype="eeg",
            suffix="eeg",
            extension=".vhdr",
        ).fpath

        if not bids_path.exists():
            print(f"Skipping {bids_path.name}: not found")
            continue

        print(f"Loading {bids_path.name} …")
        raw = mne.io.read_raw_brainvision(bids_path, preload=True)

        # Add FCz only if it isn’t already there
        if "FCz" not in raw.ch_names:
            raw = mne.add_reference_channels(raw, ref_channels=["FCz"])
        else:
            print("  ℹ️ FCz already present — skipping reference addition")

        raw.rename_channels(lambda ch: ch.replace("BrainVision RDA_", ""))
        raw.set_montage(montage)

        print(f"Overwriting original BrainVision files: {bids_path.name}")
        raw.export(bids_path, fmt="brainvision", overwrite=True)
        print(f"✅ Done: {bids_path.name}")

