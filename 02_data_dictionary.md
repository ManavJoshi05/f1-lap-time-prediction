# Data Dictionary and Leakage Register

## Target

| Column | Meaning | Unit | Availability | Use |
|---|---|---:|---|---|
| LapTimeSeconds | Duration of the target lap | seconds | After lap finishes | Prediction target only |

## Identifiers and context

| Column | Meaning | Availability before target lap? | Use |
|---|---|---:|---|
| Season | Championship year | Yes | Feature / grouping |
| RoundNumber | Event round | Yes | Grouping; avoid treating as continuous causal feature |
| EventName | Grand Prix name | Yes | Feature / grouping |
| Circuit | Circuit/location identifier | Yes | Feature |
| SessionType | FP1, FP2, FP3, Q, R, etc. | Yes | Feature |
| Driver | Driver code | Yes | Feature |
| Team | Constructor/team | Yes | Feature |
| LapNumber | Driver lap count in session | Yes | Candidate feature |
| Stint | Tyre stint identifier | Yes after classification | Feature |
| TrackStatus | Session/race status | Sometimes | Feature with careful timestamp alignment |

## Pre-lap candidate features

| Column | Meaning | Why it may help | Leakage check |
|---|---|---|---|
| Compound | Current tyre compound | Tyre grip differs by compound | Must refer to the target lap’s tyre already fitted |
| TyreLife | Tyre age before target lap | Captures degradation | Use tyre life at start of target lap |
| FreshTyre | Whether tyre is new | Captures initial grip | Must be known before target lap |
| AirTemp | Air temperature | Affects conditions | Use latest reading before lap start |
| TrackTemp | Track temperature | Affects tyre behaviour/grip | Use latest reading before lap start |
| Rainfall | Rain indicator | Captures wet conditions | Use latest reading before lap start |
| PriorLapTimeSeconds | Previous valid lap duration | Captures recent pace | Must be previous lap only |
| RollingMeanLast3 | Mean of prior 3 valid laps | Smooths recent pace | Exclude target lap |
| DriverEventHistoricalMean | Driver historical pace at same event | Driver-track familiarity proxy | Compute using training data only |
| FieldMedianPriorLap | Median previous-lap pace of active field | Track evolution proxy | Must be time-aligned and exclude target target |
| IsAccurate | Quality flag distinguishing genuine flying laps from out/in laps | Use as a filter, not a predictive feature |
| TrackStatus | Session condition code at lap time | Needs decoding before use; verify meaning per FastF1 documentation |

## Features excluded from Version 1

| Column | Why excluded |
|---|---|
| Sector1Time of target lap | It is part of the target lap duration |
| Sector2Time of target lap | It is part of the target lap duration |
| Sector3Time of target lap | It is part of the target lap duration |
| SpeedTrap of target lap | Measured during the target lap |
| Target-lap throttle/brake/speed traces | Measured during/after target lap |
| Final session classification | Unknown before the target lap ends |
| Future laps / future weather measurements | Future information leakage |
| SpeedI1, SpeedI2, SpeedFL, SpeedST | Speed-trap readings measured during the target lap |
| IsPersonalBest | Known only after the lap; not yet decided if useful for next-lap features |

## Optional Version 2 features

| Feature group | Construction |
|---|---|
| Prior-lap telemetry aggregates | Mean/max speed, throttle fraction, brake fraction, DRS fraction, gear statistics from the prior completed lap |
| Partial-lap telemetry | Data from the first 10–20 seconds or first sector of the current lap; redefine target as remaining duration or final lap duration |
| Track map features | Curvature, corner count, elevation proxy if a public reliable source is used |