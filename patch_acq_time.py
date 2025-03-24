from pathlib import Path
import pandas as pd

# BIDS dataset root
bids_root = Path("ds003846-2.0.2")
new_time = "2022-01-01T12:00:00.000"

# Go through all *_scans.tsv files
for scans_file in bids_root.rglob("*_scans.tsv"):
    df = pd.read_csv(scans_file, sep="\t")

    if "acq_time" in df.columns:
        # Only update rows NOT in the motion folder
        mask = ~df["filename"].str.startswith("motion/")
        df.loc[mask, "acq_time"] = new_time

        df.to_csv(scans_file, sep="\t", index=False)
        print(f"✔️ Patched {scans_file}")
    else:
        print(f"⚠️ Skipped {scans_file} (no acq_time column)")
