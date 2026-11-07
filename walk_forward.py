import pandas as pd
import duckdb

# Lees de historische Elia-data
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

# Maak onze twee voorspellende variabelen
data["uur"] = data["datetime"].dt.hour
data["is_weekend"] = data["datetime"].dt.dayofweek >= 5

# Definieer drie testperiodes
periodes = [
    ("2025-01-11", "2025-01-18"),
    ("2025-01-18", "2025-01-25"),
    ("2025-01-25", "2025-02-01")
]

mae_resultaten = []

for nummer, (begin, einde) in enumerate(periodes, start=1):

    test_begin = pd.Timestamp(begin, tz="Europe/Brussels")
    test_einde = pd.Timestamp(einde, tz="Europe/Brussels")

    # Training: uitsluitend gegevens vóór de testperiode
    train = data[data["datetime"] < test_begin].copy()

    # Test: de volgende zeven dagen
    test = data[
        (data["datetime"] >= test_begin) &
        (data["datetime"] < test_einde)
    ].copy()

    # Leer het gemiddelde profiel
    profiel = (
        train.groupby(["uur", "is_weekend"])["belasting_mw"]
        .mean()
        .reset_index(name="voorspelling_mw")
    )

    # Maak voorspellingen
    test = test.merge(
        profiel,
        on=["uur", "is_weekend"],
        how="left",
        validate="many_to_one"
    )

    assert test["voorspelling_mw"].notna().all()

    # Bereken de MAE van deze testperiode
    mae = (
        test["belasting_mw"] - test["voorspelling_mw"]
    ).abs().mean()

    mae_resultaten.append(mae)

    print(f"Test {nummer}")
    print("Trainingsuren:", len(train))
    print("Testuren:", len(test))
    print("MAE:", round(mae, 2), "MW\n")

# Gemiddelde fout over alle drie de testperiodes
gemiddelde_mae = sum(mae_resultaten) / len(mae_resultaten)

print("GEMIDDELDE MAE:", round(gemiddelde_mae, 2), "MW")