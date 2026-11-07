import pandas as pd
import duckdb

# Lees januari en februari
data = duckdb.sql("""
    SELECT datetime, belasting_mw
    FROM read_parquet([
        'data/elia_load_hourly_2025_01.parquet',
        'data/elia_load_hourly_2025_02.parquet'
    ])
    ORDER BY datetime
""").df()

data["datetime"] = pd.to_datetime(
    data["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

# Kalenderfeatures
data["uur"] = data["datetime"].dt.hour
data["weekdag"] = data["datetime"].dt.dayofweek
data["is_weekend"] = data["weekdag"] >= 5

# Model 5: belasting van hetzelfde uur vorige week
data["model5"] = data["belasting_mw"].shift(168)

# Vier testweken
periodes = [
    ("2025-02-01", "2025-02-08"),
    ("2025-02-08", "2025-02-15"),
    ("2025-02-15", "2025-02-22"),
    ("2025-02-22", "2025-03-01")
]

resultaten = []

for nummer, (begin, einde) in enumerate(periodes, start=1):

    start = pd.Timestamp(begin, tz="Europe/Brussels")
    stop = pd.Timestamp(einde, tz="Europe/Brussels")

    train = data[data["datetime"] < start].copy()

    test = data[
        (data["datetime"] >= start) &
        (data["datetime"] < stop)
    ].copy()

    # MODEL 2: Uur + werkdag/weekend
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

    # MODEL 7: Uur + afzonderlijke weekdag
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

    # Controleer de voorspellingen
    assert len(test) == 168
    assert test[
        ["model2", "model5", "model7"]
    ].notna().all().all()

    # Bereken de MAE per model
    mae2 = (test["belasting_mw"] - test["model2"]).abs().mean()
    mae5 = (test["belasting_mw"] - test["model5"]).abs().mean()
    mae7 = (test["belasting_mw"] - test["model7"]).abs().mean()

    resultaten.append({
        "Week": nummer,
        "Model 2": mae2,
        "Model 5": mae5,
        "Model 7": mae7
    })

tabel = pd.DataFrame(resultaten)

print("\nMAE PER TESTWEEK FEBRUARI")
print(tabel.round(2).to_string(index=False))

gemiddelden = tabel[
    ["Model 2", "Model 5", "Model 7"]
].mean()

print("\nGEMIDDELDE MAE")
print(gemiddelden.round(2))

print("\nBESTE MODEL")
print(gemiddelden.idxmin())