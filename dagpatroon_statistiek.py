import pandas as pd
import duckdb

# Lees de bestaande uurdata
data = duckdb.sql("""
    SELECT datetime, belasting_mw
    FROM read_parquet(
        'data/elia_load_hourly_2025_01.parquet'
    )
""").df()

# Gebruik Belgische tijd
data["datetime"] = pd.to_datetime(
    data["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

# Haal het uur uit de tijdstempel
data["uur"] = data["datetime"].dt.hour

# Bereken de statistieken per uur
uurprofiel = data.groupby("uur")["belasting_mw"].agg(
    ["mean", "std"]
)

uurprofiel.columns = [
    "gemiddelde_mw",
    "standaardafwijking_mw"
]

print("\nGEMIDDELD DAGPROFIEL")
print(uurprofiel.round(2))

# Zoek de hoogste en laagste belastinguren
print("\nHoogste gemiddeld belastinguur:",
      uurprofiel["gemiddelde_mw"].idxmax())

print("Laagste gemiddeld belastinguur:",
      uurprofiel["gemiddelde_mw"].idxmin())