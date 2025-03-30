import mne
from mne_icalabel import label_components
from src.config import ICA_N_COMPONENTS, ICA_RANDOM_STATE


def run_ica_label_exclude(raw_sessions, n_components=ICA_N_COMPONENTS, random_state=ICA_RANDOM_STATE):
    """
    Run ICA for each session to remove artifacts:
      1. Perform ICA (Infomax, extended, n_components).
      2. Label components using ICLabel.
      3. Exclude components not labeled as 'brain' or 'other'.
      4. Apply ICA to remove the artifact components.

    Parameters
    ----------
    raw_sessions : dict
        Dictionary with session names and corresponding mne.io.Raw objects.
    n_components : int, optional
        Number of ICA components.
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    ica_cleaned : dict
        Dictionary with session names and cleaned Raw objects.
    """
    ica_cleaned = {}
    for session, raw in raw_sessions.items():
        print(f"\n=== ICA for {session} ===")
        ica = mne.preprocessing.ICA(
            n_components=n_components,
            max_iter="auto",
            method="infomax",
            random_state=random_state,
            fit_params=dict(extended=True),
        )
        print("  Fitting ICA...")
        ica.fit(raw)
        print("  Labeling ICA components with ICLabel...")
        ic_labels = label_components(raw, ica, method="iclabel")
        labels = ic_labels["labels"]
        print(f"  ICLabel assigned: {labels}")
        exclude_idx = [idx for idx, lab in enumerate(labels) if lab not in ["brain", "other"]]
        print(f"  Excluding components: {exclude_idx}")
        if len(exclude_idx) == n_components:
            raise ValueError(f"All ICA components flagged for removal in {session}. Check data quality!")
        raw_clean = raw.copy()
        ica.apply(raw_clean, exclude=exclude_idx)
        ica_cleaned[session] = raw_clean
    return ica_cleaned
