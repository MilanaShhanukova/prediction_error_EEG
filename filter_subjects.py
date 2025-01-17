import os


def get_subjects_filtered_dir(main_dir: str):
    subjects = []

    for folder in os.listdir(main_dir):
        if folder.startswith("sub"):
            subject_path = os.path.join(main_dir, folder)
            required_subfolders = ["ses-EMS", "ses-Vibro", "ses-Visual"]
            subfolder_check = all(
                os.path.isdir(os.path.join(subject_path, subfolder))
                for subfolder in required_subfolders
            )
            if subfolder_check:
                subjects.append(folder)
            else:
                print(f"{folder} is missing one or more required subfolders.")

    return subjects
