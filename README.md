# EEG Semester Project – mne-bids-pipeline Version

This branch uses the mne-bids-pipeline to preprocess EEG data from a Prediction Error experiment.
The dataset is organized in BIDS format. The preprocessing configuration is defined in
**config_pipeline.yml**, and the pipeline is run using **run_pipeline.sh**.

## How to Run

1. **Install Dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
2. **Run the Preprocessing Pipeline:**
   \`\`\`bash
   ./run_pipeline.sh
   \`\`\`
   Preprocessed files will be saved in the output directory specified in the config file.
3. **Open the Analysis Notebook:**
   \`\`\`bash
   jupyter notebook notebooks/analysis.ipynb
   \`\`\`

