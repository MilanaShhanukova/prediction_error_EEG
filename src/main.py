#!/usr/bin/env python
import argparse
from pathlib import Path
from data_loader import load_raw_sessions
from preprocessing import preprocess_raw_sessions
from ica import run_ica_label_exclude
from sanity_checks import check_channel_statistics  # Optionally, plot_psd_sanity
import mne

def main():
    parser = argparse.ArgumentParser(description="EEG Preprocessing Pipeline")
    parser.add_argument("--base_path", type=str, required=True,
                        help="Base directory containing the dataset (e.g., ./ds003846-2.0.2).")
    parser.add_argument("--subject", type=str, required=True,
                        help="Subject identifier (e.g., sub-02).")
    parser.add_argument("--outdir", type=str, required=False, default=None,
                        help="Optional directory to save the cleaned Raw files.")
    args = parser.parse_args()

    base_path = Path(args.base_path)
    subject = args.subject
    outdir = Path(args.outdir) if args.outdir else Path("./processed_eeg_data")

    print(f"\n\n>>> Starting pipeline for {subject} <<<")

    raw_sessions = load_raw_sessions(base_path, subject)
    raw_sessions = preprocess_raw_sessions(raw_sessions)

    for session, raw in raw_sessions.items():
        check_channel_statistics(raw, session)
        # Uncomment the next line to display PSD plots:
        # plot_psd_sanity(raw, session)

    clean_sessions = run_ica_label_exclude(raw_sessions)

    if outdir:
        subject_outdir = outdir / subject
        subject_outdir.mkdir(exist_ok=True, parents=True)
        for sess, raw_clean in clean_sessions.items():
            out_path = subject_outdir / f"{sess}_cleaned_raw.fif"
            print(f"Saving cleaned {sess} data to {out_path}")
            raw_clean.save(out_path, overwrite=True)

    print("\n>>> Pipeline complete! <<<\n")

if __name__ == "__main__":
    main()
