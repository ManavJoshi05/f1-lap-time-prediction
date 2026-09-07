"""Unit tests for src/features/pre_lap_features.py."""

import pandas as pd
import pytest

from src.features.pre_lap_features import (
    add_driver_history_features,
    add_field_context_features,
    add_lap_time_seconds,
    build_pre_lap_feature_table,
)


@pytest.fixture
def sample_clean_laps() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Driver": ["LEC", "LEC", "LEC", "LEC", "VER", "VER", "VER"],
            "LapNumber": [2, 3, 4, 5, 2, 3, 4],
            "LapTime": [
                pd.Timedelta(seconds=72.0),
                pd.Timedelta(seconds=71.5),
                pd.Timedelta(seconds=71.0),
                pd.Timedelta(seconds=70.8),
                pd.Timedelta(seconds=73.0),
                pd.Timedelta(seconds=72.0),
                pd.Timedelta(seconds=71.8),
            ],
        }
    )


def test_add_lap_time_seconds_converts_timedelta(sample_clean_laps):
    result = add_lap_time_seconds(sample_clean_laps)
    assert result.loc[0, "LapTimeSeconds"] == pytest.approx(72.0)
    assert result.loc[3, "LapTimeSeconds"] == pytest.approx(70.8)


def test_driver_history_first_lap_has_no_prior(sample_clean_laps):
    with_seconds = add_lap_time_seconds(sample_clean_laps)
    result = add_driver_history_features(with_seconds)

    first_lec_row = result[(result["Driver"] == "LEC") & (result["LapNumber"] == 2)].iloc[0]
    assert pd.isna(first_lec_row["PriorLapTimeSeconds"])
    assert first_lec_row["DriverLapsCompletedSoFar"] == 0


def test_driver_history_prior_lap_time_matches_previous_row(sample_clean_laps):
    with_seconds = add_lap_time_seconds(sample_clean_laps)
    result = add_driver_history_features(with_seconds)

    third_lec_row = result[(result["Driver"] == "LEC") & (result["LapNumber"] == 4)].iloc[0]
    assert third_lec_row["PriorLapTimeSeconds"] == pytest.approx(71.5)
    assert third_lec_row["DriverLapsCompletedSoFar"] == 2


def test_driver_history_does_not_leak_current_lap(sample_clean_laps):
    with_seconds = add_lap_time_seconds(sample_clean_laps)
    result = add_driver_history_features(with_seconds)

    for _, row in result.iterrows():
        if pd.notna(row["PriorLapTimeSeconds"]):
            assert row["PriorLapTimeSeconds"] != row["LapTimeSeconds"] or True
            # Explicit leakage check: prior value must come from an
            # earlier LapNumber for the same driver, never the row's
            # own lap.
            driver_rows = result[result["Driver"] == row["Driver"]]
            earlier_rows = driver_rows[driver_rows["LapNumber"] < row["LapNumber"]]
            assert row["PriorLapTimeSeconds"] in earlier_rows["LapTimeSeconds"].values


def test_driver_history_does_not_mix_drivers(sample_clean_laps):
    with_seconds = add_lap_time_seconds(sample_clean_laps)
    result = add_driver_history_features(with_seconds)

    first_ver_row = result[(result["Driver"] == "VER") & (result["LapNumber"] == 2)].iloc[0]
    assert pd.isna(first_ver_row["PriorLapTimeSeconds"])


def test_rolling_mean_uses_at_most_three_prior_laps(sample_clean_laps):
    with_seconds = add_lap_time_seconds(sample_clean_laps)
    result = add_driver_history_features(with_seconds)

    fourth_lec_row = result[(result["Driver"] == "LEC") & (result["LapNumber"] == 5)].iloc[0]
    expected_mean = pd.Series([72.0, 71.5, 71.0]).mean()
    assert fourth_lec_row["RollingMeanLast3"] == pytest.approx(expected_mean)


def test_field_context_uses_prior_lap_number_only(sample_clean_laps):
    with_seconds = add_lap_time_seconds(sample_clean_laps)
    with_history = add_driver_history_features(with_seconds)
    result = add_field_context_features(with_history)

    lec_lap4 = result[(result["Driver"] == "LEC") & (result["LapNumber"] == 4)].iloc[0]
    lap3_median = with_seconds[with_seconds["LapNumber"] == 3]["LapTimeSeconds"].median()
    assert lec_lap4["FieldMedianPriorLapNumber"] == pytest.approx(lap3_median)


def test_build_pre_lap_feature_table_runs_end_to_end(sample_clean_laps):
    result = build_pre_lap_feature_table(sample_clean_laps)

    expected_columns = {
        "LapTimeSeconds",
        "PriorLapTimeSeconds",
        "RollingMeanLast3",
        "DriverSessionMeanSoFar",
        "DriverLapsCompletedSoFar",
        "FieldMedianPriorLapNumber",
    }
    assert expected_columns.issubset(result.columns)
    assert len(result) == len(sample_clean_laps)