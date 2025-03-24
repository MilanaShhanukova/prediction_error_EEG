from pathlib import Path
import mne
import pandas as pd
from mne_icalabel import label_components

DERIV_ROOT = Path("./bids_derivatives")

for sub_dir in sorted(DERIV_ROOT.glob("sub-*")):
    for ses_dir in sorted(sub_dir.glob("ses-*")):
        eeg_dir = ses_dir / "eeg"
        if not eeg_dir.exists():
            continue

        raw_path = next(eeg_dir.glob("*_proc-filt_raw.fif"), None)
        ica_path = next(eeg_dir.glob("*_proc-icafit_ica.fif"), None)
        if raw_path is None or ica_path is None:
            print(f"Skipping {eeg_dir.name}: missing files")
            continue

        base = raw_path.stem.replace("_proc-filt_raw", "")
        tsv_path = eeg_dir / f"{base}_proc-ica_components.tsv"
        clean_path = eeg_dir / f"{base}_proc-icaclean_raw.fif"

        raw = mne.io.read_raw_fif(raw_path, preload=True)
        ica = mne.preprocessing.read_ica(ica_path)

        # set montage so ICLabel has electrode locations
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="warn")

        # Run ICLabel
        labels = label_components(raw, ica, method="iclabel")["labels"]
        exclude = [i for i, lab in enumerate(labels) if lab not in ("brain", "other")]

        print(f"Excluded components for {base}: {exclude}")

        # Commented out to avoid interrupting batch runs
        # ica.plot_components(title=base)
        # if exclude:
        #     ica.plot_properties(raw, picks=exclude, psd_args={"fmax": 50})

        # Save TSV
        df = pd.DataFrame({
            "component": range(len(labels)),
            "exclude": [i in exclude for i in range(len(labels))],
            "label": labels
        })
        df.to_csv(tsv_path, sep="\t", index=False)
        print(f"Wrote exclusions to {tsv_path}")

        # Apply and save cleaned raw
        raw_clean = raw.copy()
        ica.apply(raw_clean, exclude=exclude)
        raw_clean.save(clean_path, overwrite=True)
        print(f"Saved cleaned raw to {clean_path}\n")
