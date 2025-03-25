# EEG Semester Project

This project replicates & extends the analysis from:

> “Detecting Visuo-Haptic Mismatches in Virtual Reality using the Prediction Error Negativity”
> [doi.org/10.1145/3290605.3300657](https://doi.org/10.1145/3290605.3300657)

## Installation

```bash
pip install -r requirements.txt
```

## Run the Pipeline

```bash
./run_pipeline.sh
```

## Analysis Steps

1. **Patch BIDS Metadata**: Fix outdated acquisition times in `_scans.tsv`.
2. **Prepare Raw EEG**: Add FCz reference and rename channels for BIDS compliance.
3. **Use MNE-BIDS-Pipeline**: Filter, re-reference, and fit ICA.
4. **Apply ICLabel**: Classify and remove unwanted ICA components on the raw data.
5. **Group Analysis**: Parse “normal” vs. “conflict” trials at FCz, compute grand averages, and plot results.
