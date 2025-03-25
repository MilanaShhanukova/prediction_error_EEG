from pathlib import Path
import mne
from mne_bids import BIDSPath

# We only overwrite the BrainVision file if we actually change something
bids_root = Path("./ds003846-2.0.2")
subjects = ["02", "06"]
sessions = ["EMS", "Vibro", "Visual"]
task = "PredictionError"

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
            print(f"Skipping {bids_path.name}: not found.")
            continue

        print(f"Loading {bids_path.name}...")
        raw = mne.io.read_raw_brainvision(bids_path, preload=True)
        changes_made = False

        # Add FCz if missing
        if "FCz" not in raw.ch_names:
            raw = mne.add_reference_channels(raw, ref_channels=["FCz"])
            changes_made = True
        else:
            print("FCz already present; no addition needed.")

        # Rename channels if needed
        old_names = raw.ch_names
        raw.rename_channels(lambda ch: ch.replace("BrainVision RDA_", ""))
        new_names = raw.ch_names
        if old_names != new_names:
            changes_made = True

        # Only export if something changed
        if changes_made:
            print(f"Overwriting {bids_path.name}...")
            raw.export(bids_path, fmt="brainvision", overwrite=True)
            print("Done.")
        else:
            print("No changes needed; skipping export.")
