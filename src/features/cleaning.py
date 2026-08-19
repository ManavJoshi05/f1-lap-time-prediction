"""Lap-level data cleaning utilities.

This module filters raw FastF1 lap tables down to genuine, usable
flying laps, removing pit-transition laps, incomplete laps, and laps
flagged as inaccurate or deleted by FastF1.
"""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "LapTime",
    "PitOutTime",
    "PitInTime",
    "IsAccurate",
    "Deleted",
]


def validate_schema(laps: pd.DataFrame) -> None:
    """Raise a clear error if expected columns are missing.

    Parameters
    ----------
    laps:
        Raw lap dataframe as returned by ``session.laps``.

    Raises
    ------
    ValueError
        If any required column is absent.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in laps.columns]
    if missing:
        raise ValueError(
            f"Lap dataframe is missing required columns: {missing}. "
            "Confirm the FastF1 session was loaded with laps=True."
        )


def filter_valid_laps(laps: pd.DataFrame) -> pd.DataFrame:
    """Return only genuine, usable flying laps.

    A lap is considered valid when all of the following hold:
    - ``LapTime`` is not null (the lap has a recorded duration).
    - ``PitOutTime`` is null (the lap did not start right after a pit stop).
    - ``PitInTime`` is null (the lap did not end with a pit stop).
    - ``IsAccurate`` is True (FastF1 marks this as a genuine flying lap).
    - ``Deleted`` is False (the lap was not deleted by race control/FIA).

    Parameters
    ----------
    laps:
        Raw lap dataframe as returned by ``session.laps``.

    Returns
    -------
    pandas.DataFrame
        A filtered copy containing only valid flying laps, with the
        original index preserved for traceability.
    """
    validate_schema(laps)

    has_lap_time = laps["LapTime"].notna()
    not_pit_out = laps["PitOutTime"].isna()
    not_pit_in = laps["PitInTime"].isna()
    is_accurate = laps["IsAccurate"] == True  # noqa: E712 (explicit bool check)
    not_deleted = laps["Deleted"].fillna(False).infer_objects(copy=False) != True

    mask = has_lap_time & not_pit_out & not_pit_in & is_accurate & not_deleted

    return laps.loc[mask].copy()


def summarize_filter_impact(laps: pd.DataFrame) -> pd.DataFrame:
    """Report how many rows each filter condition removes.

    Useful for logging and for the experiment log, so you can see
    exactly why the row count dropped from raw to clean.

    Parameters
    ----------
    laps:
        Raw lap dataframe as returned by ``session.laps``.

    Returns
    -------
    pandas.DataFrame
        One row per filter condition with the count of rows failing
        that condition.
    """
    validate_schema(laps)

    total = len(laps)
    rows = [
        {
            "condition": "Missing LapTime",
            "rows_failing": int(laps["LapTime"].isna().sum()),
        },
        {
            "condition": "Has PitOutTime (pit-out lap)",
            "rows_failing": int(laps["PitOutTime"].notna().sum()),
        },
        {
            "condition": "Has PitInTime (pit-in lap)",
            "rows_failing": int(laps["PitInTime"].notna().sum()),
        },
        {
            "condition": "IsAccurate is False",
            "rows_failing": int((laps["IsAccurate"] == False).sum()),  # noqa: E712
        },
        {
            "condition": "Deleted is True",
            "rows_failing": int((laps["Deleted"].fillna(False).infer_objects(copy=False) == True).sum()),  # noqa: E712
        },
    ]

    summary = pd.DataFrame(rows)
    summary["total_rows"] = total
    return summary