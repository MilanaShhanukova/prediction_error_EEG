# EEG Semester Project

This project replicates & extends the analysis from:

> “Detecting Visuo-Haptic Mismatches in Virtual Reality using the Prediction Error Negativity”
> [doi.org/10.1145/3290605.3300657](https://doi.org/10.1145/3290605.3300657)


## How to Run

1. **Download the dataset**

   ```bash
   ./ds003846-2.0.2.sh
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the preprocessing pipeline**

   Example for subject `sub-02`:

   ```bash
   ./run_pipeline.sh --base_path ./ds003846-2.0.2 --subject sub-02 --outdir processed_eeg_data
   ```

4. **Open the analysis notebook**

   ```bash
   jupyter notebook notebooks/group_analysis.ipynb
   ```

## Pipeline

- Load the EEG files
- Preprocess:
  - Bandpass 1–125 Hz
  - Downsample to 250 Hz
  - Average re-reference
  - Notch filter at 50 Hz
- Remove artifacts via ICA + ICLabel
- Compare ERPs across conditions (group-level, FCz focus)