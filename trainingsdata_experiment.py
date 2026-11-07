import pandas as pd
import duckdb

# Lees de uurdata van januari
data = duckdb.sql("""
    SELECT datetime, belasting_mw
    FROM read_parquet(
        'data/elia_load_hourly_2025_01.parquet'
    )
    ORDER BY datetime
""").df()

data["datetime"] = pd.to_datetime(
    data["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

data["uur"] = data["datetime"].dt.hour
data["weekdag"] = data["datetime"].dt.dayofweek

# Houd de testperiode constant
test_begin = pd.Timestamp(
    "2025-01-25", tz="Europe/Brussels"
)

test_einde = pd.Timestamp(
    "2025-02-01", tz="Europe/Brussels"
)

test = data[
    (data["datetime"] >= test_begin) &
    (data["datetime"] < test_einde)
].copy()

# Test vier hoeveelheden trainingsdata
for dagen in [7, 14, 21, 24]:

    train_begin = test_begin - pd.Timedelta(days=dagen)

    train = data[
        (data["datetime"] >= train_begin) &
        (data["datetime"] < test_begin)
    ].copy()

    # Leer het profiel van model 7
    profiel = (
        train.groupby(["uur", "weekdag"])["belasting_mw"]
        .mean()
        .reset_index(name="voorspelling_mw")
    )

    voorspellingen = test.merge(
        profiel,
        on=["uur", "weekdag"],
        how="left",
        validate="many_to_one"
    )

    assert voorspellingen["voorspelling_mw"].notna().all()

    # Bereken de MAE
    mae = (
        voorspellingen["belasting_mw"]
        - voorspellingen["voorspelling_mw"]
    ).abs().mean()

    print(
        f"Training: {dagen} dagen | "
        f"MAE: {mae:.2f} MW"
    )