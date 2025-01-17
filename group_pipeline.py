import argparse
import subprocess
import os
from filter_subjects import get_subjects_filtered_dir
from prepare_subject import prepare_subject_ica

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the prepare_subject script for each subject."
    )
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)

    script_path = "/prediction_error_EEG/prepare_subject.py"

    args = parser.parse_args()

    subjects = get_subjects_filtered_dir(main_dir=args.input_dir)

    for subject in subjects:
        # result = subprocess.run(
        #     ["python", script_path, "--subject", subject, "--base_path", args.input_dir, "--save_dir", args.output_dir],
        #     check=True,
        #     capture_output=True,
        #     text=True,
        # )

        prepare_subject_ica(
            base_path=args.input_dir, save_dir=args.output_dir, subject=subject
        )
