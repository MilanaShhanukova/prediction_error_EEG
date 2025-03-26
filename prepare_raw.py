from pathlib import Path
import pandas as pd
import mne
from mne_bids import BIDSPath

bids_root = Path("./ds003846-2.0.2")
subjects = ["02", "06"]
sessions = ["EMS", "Vibro", "Visual"]
task = "PredictionError"

for sub in subjects:
    for ses in sessions:
        # EEG data path (.vhdr)
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

        print(f"\n--- Processing {bids_path.name} ---")
        raw = mne.io.read_raw_brainvision(bids_path, preload=True)
        changes_made = False

        # Add FCz if not present
        if "FCz" not in raw.ch_names:
            raw = mne.add_reference_channels(raw, ref_channels=["FCz"])
            changes_made = True
        else:
            print("FCz already present")

        # Rename BrainVision RDA_ channels
        old_names = raw.ch_names
        raw.rename_channels(lambda ch: ch.replace("BrainVision RDA_", ""))
        if raw.ch_names != old_names:
            changes_made = True
            print("Channel names cleaned")

        # TODO: Remove
        # Handle events.tsv using BIDSPath
        # events_path = BIDSPath(
        #     subject=sub,
        #     session=ses,
        #     task=task,
        #     suffix="events",
        #     datatype="eeg",
        #     extension=".tsv",
        #     root=bids_root,
        # ).fpath

        # if events_path.exists():
        #     print(f"Checking events file: {events_path.name}")
        #     df = pd.read_csv(events_path, sep="\t")

        #     # If trial_type already exists, skip rewriting
        #     if False:
        #         print("trial_type column already exists — skipping modification.")
        #     else:
        #         print("Adding trial_type column...")

        #         # The BIDS pipeline expects a trial_type column
        #         # Our condition label ('normal' or 'conflict') is hidden in the 'value' string,
        #         # so we extract it and store it in trial_type for proper condition parsing.
        #         def extract_trial_type(row):
        #             if row.get("type") == "box:touched":
        #                 for item in str(row.get("value", "")).split(";"):
        #                     if "normal_or_conflict" in item:
        #                         return item.split(":")[1]
        #             return "n/a"

        #         df["trial_type"] = df.apply(extract_trial_type, axis=1)
        #         df.to_csv(events_path, sep="\t", index=False)
        #         print("trial_type column written to events.")
        # else:
        #     print(f"No events file found: {events_path.name}")

        # Export raw EEG if changes were made
        if changes_made:
            print(f"Saving updated raw to {bids_path.name}...")
            raw.export(bids_path, fmt="brainvision", overwrite=True)
            print("Export complete")
        else:
            print("No raw changes to save")
