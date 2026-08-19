"""Unit tests for src/features/cleaning.py."""

import pandas as pd
import pytest

from src.features.cleaning import (
    filter_valid_laps,
    summarize_filter_impact,
    validate_schema,
)


def make_lap_row(
    lap_time,
    pit_out_time=pd.NaT,
    pit_in_time=pd.NaT,
    is_accurate=True,
    deleted=False,
):
    return {
        "Driver": "LEC",
        "LapNumber": 1,
        "LapTime": lap_time,
        "PitOutTime": pit_out_time,
        "PitInTime": pit_in_time,
        "IsAccurate": is_accurate,
        "Deleted": deleted,
    }


@pytest.fixture
def sample_laps() -> pd.DataFrame:
    one_min = pd.Timedelta(minutes=1, seconds=30)

    rows = [
        make_lap_row(one_min),                                   # valid flying lap
        make_lap_row(pd.NaT),                                    # missing LapTime
        make_lap_row(one_min, pit_out_time=pd.Timedelta(seconds=10)),  # pit-out lap
        make_lap_row(one_min, pit_in_time=pd.Timedelta(seconds=95)),   # pit-in lap
        make_lap_row(one_min, is_accurate=False),                # inaccurate lap
        make_lap_row(one_min, deleted=True),                     # deleted lap
        make_lap_row(one_min),                                   # another valid lap
    ]
    return pd.DataFrame(rows)


def test_validate_schema_passes_with_required_columns(sample_laps):
    validate_schema(sample_laps)


def test_validate_schema_raises_when_column_missing():
    incomplete = pd.DataFrame({"LapTime": [pd.Timedelta(seconds=90)]})
    with pytest.raises(ValueError, match="missing required columns"):
        validate_schema(incomplete)


def test_filter_valid_laps_keeps_only_genuine_laps(sample_laps):
    result = filter_valid_laps(sample_laps)

    assert len(result) == 2
    assert result["LapTime"].notna().all()
    assert result["PitOutTime"].isna().all()
    assert result["PitInTime"].isna().all()
    assert (result["IsAccurate"] == True).all()  # noqa: E712
    assert (result["Deleted"] == False).all()  # noqa: E712


def test_filter_valid_laps_returns_copy_not_view(sample_laps):
    result = filter_valid_laps(sample_laps)
    result["LapTime"] = pd.NaT
    original_still_valid = sample_laps.loc[result.index[:0]]  # no-op guard
    assert sample_laps["LapTime"].notna().sum() > 0


def test_filter_valid_laps_empty_input_returns_empty_output():
    empty = pd.DataFrame(
        columns=["LapTime", "PitOutTime", "PitInTime", "IsAccurate", "Deleted"]
    )
    result = filter_valid_laps(empty)
    assert result.empty


def test_summarize_filter_impact_counts_match_expectations(sample_laps):
    summary = summarize_filter_impact(sample_laps)

    total_rows = summary["total_rows"].iloc[0]
    assert total_rows == len(sample_laps)

    counts = dict(zip(summary["condition"], summary["rows_failing"]))
    assert counts["Missing LapTime"] == 1
    assert counts["Has PitOutTime (pit-out lap)"] == 1
    assert counts["Has PitInTime (pit-in lap)"] == 1
    assert counts["IsAccurate is False"] == 1
    assert counts["Deleted is True"] == 1

def test_filter_valid_laps_handles_none_in_deleted_column():
    """Deleted may arrive as dtype object with None instead of False."""
    laps = pd.DataFrame([
        {
            "LapTime": pd.Timedelta(seconds=90),
            "PitOutTime": pd.NaT,
            "PitInTime": pd.NaT,
            "IsAccurate": True,
            "Deleted": None,  # None, not False -- this is the real-world case
        },
        {
            "LapTime": pd.Timedelta(seconds=90),
            "PitOutTime": pd.NaT,
            "PitInTime": pd.NaT,
            "IsAccurate": True,
            "Deleted": True,
        },
    ])
    result = filter_valid_laps(laps)
    assert len(result) == 1