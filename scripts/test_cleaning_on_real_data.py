from pathlib import Path
import sys

import fastf1
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.cleaning import filter_valid_laps, summarize_filter_impact

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "raw" / "fastf1_cache"

fastf1.Cache.enable_cache(str(CACHE_DIR))

session = fastf1.get_session(2024, "Monaco", "Q")
session.load(telemetry=False, weather=False, messages=False)

laps = session.laps

print("Filter impact:")
print(summarize_filter_impact(laps).to_string(index=False))

clean_laps = filter_valid_laps(laps)
print(f"\nRaw rows: {len(laps)}")
print(f"Clean rows: {len(clean_laps)}")
print(f"\nClean lap sample:\n{clean_laps[['Driver', 'LapNumber', 'LapTime']].head(10)}")