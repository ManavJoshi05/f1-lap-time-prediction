# Modeling Protocol

## Prediction task
Predict `LapTimeSeconds` for a valid Formula 1 lap using only information available before that lap begins.

## Data quality filters
Exclude:
- Missing lap-time target.
- Pit-out laps.
- Pit-in laps where identifiable.
- Laps with clearly invalid/deleted timing.
- Laps affected by exceptional session conditions where consistent filtering is possible.
- Observations with missing essential features.

## Split strategy
Use group-based splits by event/session. Do not randomly split rows.

Recommended first split:
- Training: earlier events/seasons.
- Validation: later events from the training season.
- Test: entirely held-out events or the next season.

Reason:
Random row splits let nearly identical laps from the same session appear in both train and test data, causing overly optimistic performance estimates.

## Baselines
1. Track-session average lap time.
2. Driver-session historical average using prior valid laps only.
3. Ridge regression.
4. Tree-based gradient boosting model.

## Metrics
- MAE in seconds: primary metric for interpretability.
- RMSE in seconds: penalizes large errors.
- R²: secondary descriptive metric.
- Per-group MAE: driver, circuit, session type, tyre compound, tyre-life band.

## Required visual checks
- Actual versus predicted scatter plot.
- Residual distribution.
- Residuals versus lap number and tyre life.
- Error by circuit and driver.
- Feature importance / SHAP summary.
- Worst-predicted laps table with explanation.

## Acceptance criteria
A final model is acceptable only if:
- It outperforms the baseline on the untouched test events.
- No target-lap sector, target-lap telemetry, or future data was used.
- Its weaknesses and limitations are documented.