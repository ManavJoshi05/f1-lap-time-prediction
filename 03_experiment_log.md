# Experiment Log

## Rules
- Log every model run that produces a reportable result.
- Record the exact dataset version, split, code commit, parameters, and metrics.
- Do not overwrite previous results.

| ID | Date | Git commit | Dataset version | Target | Features | Split | Model | MAE (s) | RMSE (s) | R² | Notes |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|
| EXP-001 | YYYY-MM-DD | commit-id | v0.1 | LapTimeSeconds | Track + driver + session mean | Held-out events | Track-session mean | | | | Baseline |
| EXP-002 | YYYY-MM-DD | commit-id | v0.1 | LapTimeSeconds | Baseline feature set | Held-out events | Ridge | | | | |
| EXP-003 | YYYY-MM-DD | commit-id | v0.1 | LapTimeSeconds | Baseline + tyre/weather/history | Held-out events | HistGradientBoosting | | | | |

## Data quality notes
- FastF1's `Deleted` column returns dtype `object` with `None` for "not deleted" laps in some sessions, rather than boolean `False`. Direct `== False` comparisons silently fail. Fixed by using `.fillna(False) != True`.