import pandas as pd
import duckdb

# Lees januari en februari samen
data = duckdb.sql("""
    SELECT datetime, belasting_mw
    FROM read_parquet([
        'data/elia_load_hourly_2025_01.parquet',
        'data/elia_load_hourly_2025_02.parquet'
    ])
    ORDER BY datetime
""").df()

# Verwerk tijdstippen
data["datetime"] = pd.to_datetime(
    data["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

data["uur"] = data["datetime"].dt.hour
data["weekdag"] = data["datetime"].dt.dayofweek
data["is_weekend"] = data["weekdag"] >= 5

# Model 5: hetzelfde uur vorige week
data["model5"] = data["belasting_mw"].shift(168)

# Chronologische splitsing
grens = pd.Timestamp(
    "2025-02-01", tz="Europe/Brussels"
)

einde = pd.Timestamp(
    "2025-02-08", tz="Europe/Brussels"
)

train = data[data["datetime"] < grens].copy()

test = data[
    (data["datetime"] >= grens) &
    (data["datetime"] < einde)
].copy()

print("Trainingsuren:", len(train))
print("Testuren:", len(test))

# Model 2: uur + werkdag/weekend
profiel2 = (
    train.groupby(["uur", "is_weekend"])["belasting_mw"]
    .mean()
    .reset_index(name="model2")
)

test = test.merge(
    profiel2,
    on=["uur", "is_weekend"],
    how="left",
    validate="many_to_one"
)

# Model 7: uur + afzonderlijke weekdag
profiel7 = (
    train.groupby(["uur", "weekdag"])["belasting_mw"]
    .mean()
    .reset_index(name="model7")
)

test = test.merge(
    profiel7,
    on=["uur", "weekdag"],
    how="left",
    validate="many_to_one"
)

# Controleer dat alle voorspellingen beschikbaar zijn
assert len(train) == 744
assert len(test) == 168
assert test[["model2", "model5", "model7"]].notna().all().all()

# Vergelijk de drie modellen
print("\nFORECASTRESULTATEN FEBRUARI")

for model in ["model2", "model5", "model7"]:
    fout = test["belasting_mw"] - test[model]

    mae = fout.abs().mean()

    print(f"{model}: MAE = {mae:.2f} MW")