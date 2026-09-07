"""Pre-lap feature engineering.

Builds features that are known before a target lap begins, using only
information from earlier laps in the same session. This module must
never use data from the target lap itself (its own sector times,
telemetry, or final classification), since that would leak the target.
"""

from __future__ import annotations

import pandas as pd


def add_lap_time_seconds(laps: pd.DataFrame) -> pd.DataFrame:
    """Add a numeric LapTimeSeconds column derived from LapTime.

    Parameters
    ----------
    laps:
        A lap dataframe containing a ``LapTime`` timedelta column.

    Returns
    -------
    pandas.DataFrame
        A copy with an added ``LapTimeSeconds`` float column.
    """
    result = laps.copy()
    result["LapTimeSeconds"] = result["LapTime"].dt.total_seconds()
    return result


def add_driver_history_features(clean_laps: pd.DataFrame) -> pd.DataFrame:
    if "LapTimeSeconds" not in clean_laps.columns:
        raise ValueError(
            "LapTimeSeconds column is required. Call add_lap_time_seconds first."
        )

    result = clean_laps.sort_values(["Driver", "LapNumber"]).copy()
    grouped = result.groupby("Driver")["LapTimeSeconds"]

    def _rolling_mean_last_3(lap_times: pd.Series) -> pd.Series:
        return lap_times.shift(1).rolling(window=3, min_periods=1).mean()

    result["PriorLapTimeSeconds"] = grouped.shift(1)
    result["RollingMeanLast3"] = (
        grouped.apply(_rolling_mean_last_3).reset_index(drop=True).values
    )
    result["DriverSessionMeanSoFar"] = (
        grouped.apply(lambda s: s.shift(1).expanding(min_periods=1).mean())
        .reset_index(drop=True)
        .values
    )
    result["DriverLapsCompletedSoFar"] = grouped.cumcount()

    return result


def add_field_context_features(clean_laps_with_history: pd.DataFrame) -> pd.DataFrame:
    """Add field-level pre-lap context features.

    Computes the median lap time recorded by all drivers at the
    preceding lap number, as a rough proxy for track evolution and
    overall pace level at that point in the session. This uses only
    laps from LapNumber - 1 or earlier, so it does not leak the
    target lap's own performance.

    Parameters
    ----------
    clean_laps_with_history:
        Output of ``add_driver_history_features``. Must include
        ``LapNumber`` and ``LapTimeSeconds``.

    Returns
    -------
    pandas.DataFrame
        A copy with an added ``FieldMedianPriorLapNumber`` column.
    """
    result = clean_laps_with_history.copy()

    median_by_lap_number = (
        result.groupby("LapNumber")["LapTimeSeconds"].median().rename("FieldMedianThisLapNumber")
    )

    lap_number_lookup = median_by_lap_number.reindex(
        result["LapNumber"] - 1
    ).reset_index(drop=True)
    lap_number_lookup.index = result.index

    result["FieldMedianPriorLapNumber"] = lap_number_lookup.values

    return result


def build_pre_lap_feature_table(clean_laps: pd.DataFrame) -> pd.DataFrame:
    """Run the full pre-lap feature pipeline on already-cleaned laps.

    Parameters
    ----------
    clean_laps:
        Output of ``filter_valid_laps`` from ``src.features.cleaning``.

    Returns
    -------
    pandas.DataFrame
        A feature-ready table with target (``LapTimeSeconds``) and all
        pre-lap features. Rows with no prior lap history for that
        driver will have NaN in lag-dependent columns and should be
        handled explicitly (drop or impute) in the modeling stage.
    """
    with_seconds = add_lap_time_seconds(clean_laps)
    with_history = add_driver_history_features(with_seconds)
    with_field_context = add_field_context_features(with_history)
    return with_field_context