import pandas as pd
import duckdb
from data_validatie import controleer_energiedata

# STAP 1: Lees de echte Elia-belastinggegevens
belasting = duckdb.sql("""
    SELECT datetime, totalload
    FROM read_parquet('data/elia_load_2025_01.parquet')
    ORDER BY datetime
""").df()

# Zet tijdstippen om naar Belgische tijd
belasting["datetime"] = pd.to_datetime(
    belasting["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

# Zet kwartiermetingen om naar uurgemiddelden
uurbelasting = (
    belasting
    .set_index("datetime")["totalload"]
    .resample("1h")
    .mean()
    .reset_index(name="belasting_mw")
)

# STAP 2: Maak fictieve uurprijzen
prijzen = pd.DataFrame({
    "datetime": pd.to_datetime([
        "2025-01-01 00:00",
        "2025-01-01 01:00"
    ]).tz_localize("Europe/Brussels"),

    "prijs_eur_mwh": [75.0, 80.0]
})

# STAP 3: Combineer de datasets
gecombineerd = pd.merge(
    uurbelasting,
    prijzen,
    on="datetime",
    how="left",
    validate="one_to_one"
)

# STAP 4: Controleer het resultaat
print(gecombineerd.head(5).round(2))

print("\nTotaal aantal uren:", len(gecombineerd))

print(
    "Uren met een prijs:",
    gecombineerd["prijs_eur_mwh"].notna().sum()
)

# Tel ontbrekende prijzen
ontbrekende_prijzen = gecombineerd["prijs_eur_mwh"].isna().sum()

# Bereken hoeveel procent van de prijzen ontbreekt
percentage_ontbrekend = (
    ontbrekende_prijzen / len(gecombineerd)
) * 100

print("\nDATAKWALITEIT PRIJZEN")
print("Ontbrekende prijzen:", ontbrekende_prijzen)
print("Percentage ontbrekend:", round(percentage_ontbrekend, 2), "%")

# Selecteer uitsluitend uren met een geldige prijs
complete_data = gecombineerd.dropna(
    subset=["prijs_eur_mwh"]
)

print("\nCOMPLETE OBSERVATIES")
print("Aantal bruikbare uren:", len(complete_data))
print(complete_data)

controleer_energiedata(gecombineerd)
