from pathlib import Path
import sys

import fastf1

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.cleaning import filter_valid_laps
from src.features.pre_lap_features import build_pre_lap_feature_table

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "raw" / "fastf1_cache"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"

fastf1.Cache.enable_cache(str(CACHE_DIR))

session = fastf1.get_session(2024, "Monaco", "Q")
session.load(telemetry=False, weather=False, messages=False)

clean_laps = filter_valid_laps(session.laps)
feature_table = build_pre_lap_feature_table(clean_laps)

columns_to_show = [
    "Driver", "LapNumber", "LapTimeSeconds",
    "PriorLapTimeSeconds", "RollingMeanLast3",
    "DriverSessionMeanSoFar", "DriverLapsCompletedSoFar",
    "FieldMedianPriorLapNumber",
]

print(feature_table[columns_to_show].head(20).to_string(index=False))
print(f"\nTotal rows: {len(feature_table)}")
print(f"\nRows with no prior lap (NaN PriorLapTimeSeconds): {feature_table['PriorLapTimeSeconds'].isna().sum()}")

output_path = OUTPUT_DIR / "2024_monaco_Q_features.parquet"
feature_table.to_parquet(output_path, index=False)
print(f"\nSaved to: {output_path}")