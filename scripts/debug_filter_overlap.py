from pathlib import Path
import sys

import fastf1
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "raw" / "fastf1_cache"

fastf1.Cache.enable_cache(str(CACHE_DIR))

session = fastf1.get_session(2024, "Monaco", "Q")
session.load(telemetry=False, weather=False, messages=False)

laps = session.laps.copy()

has_lap_time = laps["LapTime"].notna()
not_pit_out = laps["PitOutTime"].isna()
not_pit_in = laps["PitInTime"].isna()
is_accurate = laps["IsAccurate"] == True
not_deleted = laps["Deleted"] == False

print("=== Individual condition counts ===")
print(f"has_lap_time:  {has_lap_time.sum()}")
print(f"not_pit_out:   {not_pit_out.sum()}")
print(f"not_pit_in:    {not_pit_in.sum()}")
print(f"is_accurate:   {is_accurate.sum()}")
print(f"not_deleted:   {not_deleted.sum()}")

print("\n=== Pairwise overlaps ===")
print(f"has_lap_time & is_accurate:              {(has_lap_time & is_accurate).sum()}")
print(f"has_lap_time & not_pit_out:               {(has_lap_time & not_pit_out).sum()}")
print(f"has_lap_time & not_pit_in:                {(has_lap_time & not_pit_in).sum()}")
print(f"is_accurate & not_pit_out:                {(is_accurate & not_pit_out).sum()}")
print(f"is_accurate & not_pit_in:                 {(is_accurate & not_pit_in).sum()}")
print(f"not_pit_out & not_pit_in:                 {(not_pit_out & not_pit_in).sum()}")

print("\n=== Crosstab: IsAccurate vs has any pit event ===")
has_pit_event = laps["PitOutTime"].notna() | laps["PitInTime"].notna()
print(pd.crosstab(laps["IsAccurate"], has_pit_event, dropna=False))

print("\n=== Sample of accurate laps (should NOT be pit laps) ===")
accurate_sample = laps.loc[is_accurate, ["Driver", "LapNumber", "LapTime", "PitOutTime", "PitInTime", "TrackStatus", "Deleted"]].head(10)
print(accurate_sample.to_string(index=False))

print("\n=== dtypes check ===")
print(laps[["LapTime", "PitOutTime", "PitInTime", "IsAccurate", "Deleted"]].dtypes)