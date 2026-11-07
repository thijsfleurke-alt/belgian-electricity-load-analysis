import pandas as pd
import duckdb

# Lees gegevens rechtstreeks uit Parquet
data = duckdb.sql("""
    SELECT datetime, totalload
    FROM read_parquet('data/elia_load_2025_01.parquet')
    ORDER BY datetime
""").df()

# Zorg voor correcte Belgische tijd
data["datetime"] = pd.to_datetime(
    data["datetime"],
    utc=True
).dt.tz_convert("Europe/Brussels")

# Gebruik datetime als index
data = data.set_index("datetime")

# Groepeer kwartiermetingen per uur
uurdata = data["totalload"].resample("1h").agg(
    ["mean", "sum", "count"]
)

# Bereken vermogen en energie
uurdata["vermogen_mw"] = uurdata["mean"]
uurdata["energie_mwh"] = uurdata["sum"] * 0.25

# Herbenoem de telling
uurdata["aantal_kwartieren"] = uurdata["count"]

# Toon de eerste vijf uren
print(
    uurdata[
        ["vermogen_mw", "energie_mwh", "aantal_kwartieren"]
    ].head(5).round(2)
)

# Bereken totale energie over januari
totale_energie_mwh = uurdata["energie_mwh"].sum()

totale_energie_gwh = totale_energie_mwh / 1000
totale_energie_twh = totale_energie_mwh / 1000000

# Controleer of alle uren volledig zijn
aantal_uren = len(uurdata)

onvolledige_uren = (
    uurdata["aantal_kwartieren"] != 4
).sum()

# Bereken energie ook rechtstreeks uit kwartierdata
controle_mwh = data["totalload"].sum() * 0.25

print("\nMAANDANALYSE JANUARI 2025")
print("Aantal uren:", aantal_uren)
print("Onvolledige uren:", onvolledige_uren)

print("Totale energie (MWh):", round(totale_energie_mwh, 2))
print("Totale energie (GWh):", round(totale_energie_gwh, 2))
print("Totale energie (TWh):", round(totale_energie_twh, 4))

print("Controle via kwartierdata:", round(controle_mwh, 2))