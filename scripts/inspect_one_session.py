from pathlib import Path
import sys

import fastf1
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "data" / "raw" / "fastf1_cache"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"

YEAR = 2024
EVENT = "Monaco"
SESSION_TYPE = "Q"


def to_seconds(value: object) -> float | None:
    if pd.isna(value):
        return None
    return value.total_seconds()


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fastf1.Cache.enable_cache(str(CACHE_DIR))

    print(f"Loading {YEAR} {EVENT} {SESSION_TYPE}...")
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load(telemetry=False, weather=True, messages=True)

    laps = session.laps.copy()

    print("\n=== Session metadata ===")
    print(f"Event: {session.event['EventName']}")
    print(f"Session: {session.name}")
    print(f"Rows in raw lap table: {len(laps)}")
    print(f"Number of columns: {len(laps.columns)}")

    print("\n=== Available columns ===")
    for column in laps.columns:
        print(column)

    preferred_columns = [
        "Driver", "Team", "LapNumber", "LapTime", "Stint",
        "Compound", "TyreLife", "FreshTyre",
        "PitOutTime", "PitInTime", "TrackStatus",
        "Deleted", "IsAccurate",
        "Sector1Time", "Sector2Time", "Sector3Time",
    ]
    existing_columns = [col for col in preferred_columns if col in laps.columns]
    preview = laps[existing_columns].copy()

    if "LapTime" in preview.columns:
        preview["LapTimeSeconds"] = preview["LapTime"].apply(to_seconds)

    print("\n=== First 15 laps ===")
    print(preview.head(15).to_string(index=False))

    print("\n=== Missing values ===")
    print(preview.isna().sum().sort_values(ascending=False).to_string())

    preview_path = OUTPUT_DIR / f"{YEAR}_{EVENT.lower()}_{SESSION_TYPE}_raw_laps_preview.csv"
    preview.to_csv(preview_path, index=False)

    schema_path = OUTPUT_DIR / f"{YEAR}_{EVENT.lower()}_{SESSION_TYPE}_schema.txt"
    with schema_path.open("w", encoding="utf-8") as file:
        file.write("FastF1 lap-table schema\n=======================\n\n")
        file.write(f"Event: {session.event['EventName']}\n")
        file.write(f"Session: {session.name}\n")
        file.write(f"Raw rows: {len(laps)}\n\n")
        for column, dtype in laps.dtypes.items():
            file.write(f"{column}: {dtype}\n")

    print(f"\nSaved preview to: {preview_path}")
    print(f"Saved schema to: {schema_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nFastF1 session inspection failed: {error}", file=sys.stderr)
        raise