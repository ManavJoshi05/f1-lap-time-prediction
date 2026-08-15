# F1 Telemetry-Based Lap Time Prediction

## Goal
Develop a reproducible machine-learning pipeline that predicts the duration of a Formula 1 lap using public historical session data.

## Primary research question
How accurately can lap time be predicted using information available before a lap starts, including driver identity, circuit/session context, tyre condition, weather, prior-lap performance, and aggregated historical telemetry features?

## Initial scope
- Data source: FastF1.
- Sessions: begin with qualifying sessions from selected seasons, then extend to race sessions.
- Prediction target: `LapTimeSeconds`.
- Unit of prediction: one valid lap by one driver.
- Initial models: naive baseline, Ridge regression, HistGradientBoostingRegressor or XGBoost.
- Evaluation: event/session-based holdout split, MAE, RMSE, R², residual analysis.

## Explicitly excluded from Version 1
- Live real-time prediction.
- Direct prediction from full raw telemetry sequences.
- Pit strategy optimization.
- Race finishing-position prediction.
- Claims of matching actual F1 team performance engineering.

## Version 2 extension
Use telemetry measured before the target lap or telemetry from the early portion of a target lap to estimate final lap time / lap-time delta.

## Definition of success
1. A script can reproduce the dataset from public sources.
2. The model beats a track-session mean baseline on held-out events.
3. Results are reported honestly by circuit, session type, driver, and tyre state.
4. The repository contains clear documentation, tests, visualizations, and reproducible commands.

## Risks and limitations
- Public data does not include full car setup, exact fuel load, all tyre state variables, and private team data.
- Race laps can be distorted by traffic, safety cars, virtual safety cars, red flags, blue flags, and pit transitions.
- Results may not generalize from qualifying to races.
- Sector times from the same target lap are target leakage for full-lap prediction.