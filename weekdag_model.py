import pandas as pd
import duckdb

# Lees de bestaande Elia-uurdata
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

# Maak kalenderfeatures
data["uur"] = data["datetime"].dt.hour
data["weekdag"] = data["datetime"].dt.dayofweek
data["is_weekend"] = data["weekdag"] >= 5

# Dezelfde testperiodes als onze eerdere backtest
periodes = [
    ("2025-01-11", "2025-01-18"),
    ("2025-01-18", "2025-01-25"),
    ("2025-01-25", "2025-02-01")
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

    # MODEL 2: Gemiddeld profiel per uur en dagtype
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

    # MODEL 7: Gemiddeld profiel per uur en weekdag
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

    # Controleer of alle voorspellingen beschikbaar zijn
    assert test[["model2", "model7"]].notna().all().all()

    # Vergelijk de voorspellingsfouten
    mae2 = (
        test["belasting_mw"] - test["model2"]
    ).abs().mean()

    mae7 = (
        test["belasting_mw"] - test["model7"]
    ).abs().mean()

    resultaten.append({
        "Test": nummer,
        "Model 2": mae2,
        "Model 7": mae7
    })

tabel = pd.DataFrame(resultaten)

print("\nMAE PER TESTWEEK (MW)")
print(tabel.round(2).to_string(index=False))

print("\nGEMIDDELDE MAE")
print(tabel[["Model 2", "Model 7"]].mean().round(2))