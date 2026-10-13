# Belgian Electricity Load Analysis

## Project overview

This project analyses historical electricity demand in Belgium using Python and publicly available data from Elia, the Belgian electricity transmission system operator.

The objective is to identify daily electricity demand patterns, investigate differences between weekdays and weekends, and develop a foundation for future energy forecasting models.

## Data source

- **Source:** Elia Open Data
- **Dataset:** Measured and forecasted total load on the Belgian grid (Historical data), `ods001`
- **Period:** 1 January 2025 – 31 January 2025
- **Resolution:** 15 minutes
- **Observations:** 2,976
- **Main variable:** Total Load (MW)

Dataset: https://opendata.elia.be/explore/dataset/ods001/

## Technologies

- Python 3.13
- pandas — data processing and statistical analysis
- matplotlib — data visualisation

## Methodology

1. Import historical electricity load data from CSV.
2. Clean column names and convert timestamps.
3. Validate data completeness and detect duplicate timestamps.
4. Calculate average, minimum and maximum electricity load.
5. Identify the average daily demand profile.
6. Compare electricity consumption patterns on weekdays and weekends.
7. Calculate hourly differences between both groups.

## Key results

| Indicator | Result |
|---|---:|
| Average electricity load | 10,454.63 MW |
| Minimum electricity load | 7,146.35 MW |
| Maximum electricity load | 13,068.81 MW |
| Average weekday load | 10,668.69 MW |
| Average weekend load | 9,839.19 MW |
| Absolute weekday/weekend difference | 829.50 MW |
| Average weekend difference | −7.78% |
| Largest hourly weekend difference | −16.40% at 07:00 |

## Main findings

**Daily demand patterns:** Electricity demand follows a recurring daily pattern, with low demand during the night and higher demand during daytime and early evening hours.

**Weekday versus weekend:** Average weekend electricity demand is approximately 7.8% lower than on weekdays.

**Hourly variation:** The weekday/weekend difference varies substantially throughout the day. The largest relative difference occurs around 07:00, when average weekend demand is approximately 16.4% lower.

**Forecasting implications:** Using a single weekend correction factor may be insufficient. Hour-specific weekday/weekend effects could help improve a future forecasting model.

## Visualisations

The project includes four visualisations:

- `elia_januari_2025.png` — historical electricity load during January 2025
- `elia_dagprofiel_2025.png` — average daily electricity load profile
- `elia_werkdagen_weekends.png` — comparison between weekdays and weekends
- `elia_weekendverschil_per_uur.png` — hourly percentage difference

## How to run

1. Install Python 3.13.
2. Install dependencies: `python -m pip install pandas matplotlib`
3. Download the original `ods001` dataset from Elia for January 2025.
4. Save the CSV file as `elia_2025.csv` in the project folder.
5. Run `analyse_elia.py` using the Python interpreter in VS Code.

## Limitations

This analysis covers only January 2025 and therefore does not represent seasonal electricity demand patterns over an entire year.

Public holidays are currently classified according to their calendar weekday. Weather conditions, industrial production schedules and other potential drivers have not been included.

The observed patterns are descriptive and do not establish causal relationships.

## Future development

This project will be extended with:

- Additional historical electricity data
- Weather and calendar features
- Time-series forecasting models
- Forecast accuracy evaluation
- Scenario analysis

## Author

Independent Python energy analytics portfolio project.