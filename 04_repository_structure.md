# Repository Structure

f1-lap-time-prediction/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── configs/
│   ├── data_config.yaml
│   └── model_config.yaml
├── data/
│   ├── raw/                 # Git ignored: cached source data
│   ├── interim/             # Git ignored: intermediate tables
│   └── processed/           # Git ignored or release-managed Parquet datasets
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_validation.ipynb
│   └── 03_model_analysis.ipynb
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── collect_fastf1.py
│   │   ├── validate_raw_data.py
│   │   └── build_lap_dataset.py
│   ├── features/
│   │   ├── cleaning.py
│   │   ├── pre_lap_features.py
│   │   └── telemetry_aggregation.py
│   ├── models/
│   │   ├── baselines.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── explain.py
│   ├── visualization/
│   │   └── plots.py
│   └── app/
│       └── streamlit_app.py
├── tests/
│   ├── test_cleaning.py
│   ├── test_features.py
│   └── test_no_leakage.py
├── reports/
│   ├── figures/
│   └── final_report.md
└── scripts/
    ├── download_data.py
    ├── train_model.py
    └── run_dashboard.py