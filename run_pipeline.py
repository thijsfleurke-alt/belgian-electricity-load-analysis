from pathlib import Path

import pandas as pd
import duckdb

from elia_download import haal_elia_data_op
from data_validatie import controleer_uurbelasting

# Kies welke maand je wilt verwerken
jaar = 2025
maand = 10

# Bereken automatisch begin- en einddatum
startdatum = pd.Timestamp(
    year=jaar, month=maand, day=1
)

einddatum = startdatum + pd.DateOffset(months=1)

start = startdatum.strftime("%Y-%m-%d")
einde = einddatum.strftime("%Y-%m-%d")

print("Periode:", start, "tot", einde)

# 1. Download de ruwe data
print("START ELIA DATA PIPELINE")

data = haal_elia_data_op(start, einde)

# 2. Verwerk de tijdstippen
data["datetime"] = pd.to_datetime(
    data["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

kwartierdata = data.set_index("datetime")["totalload"]

# 3. Zet kwartiermetingen om naar uurgegevens
uurdata = kwartierdata.resample("1h").agg(
    ["mean", "sum", "count"]
)

uurdata = uurdata.rename(columns={
    "mean": "belasting_mw",
    "count": "aantal_kwartieren"
})

uurdata["energie_mwh"] = uurdata["sum"] * 0.25

uurdata = uurdata.drop(columns="sum").reset_index()

# 4. Controleer de datakwaliteit
controleer_uurbelasting(uurdata)

# Controleer het energiebehoud
energie_kwartier = kwartierdata.sum() * 0.25
energie_uur = uurdata["energie_mwh"].sum()

assert abs(energie_kwartier - energie_uur) < 0.001, \
    "Energiereconciliatie mislukt"

# 5. Sla gevalideerde data op als Parquet
Path("data").mkdir(exist_ok=True)

con = duckdb.connect()
con.register("uurdata", uurdata)
bestand = f"data/elia_load_hourly_{jaar}_{maand:02d}.parquet"

con.execute(f"""
    COPY (
        SELECT
            datetime,
            belasting_mw,
            energie_mwh,
            aantal_kwartieren
        FROM uurdata
    )
    TO '{bestand}'
    (FORMAT PARQUET)
""")

aantal_opgeslagen = con.execute("""
    SELECT COUNT(*)
    FROM read_parquet(?)
""", [bestand]).fetchone()[0]

con.close()

# 6. Toon het eindresultaat
print("\nPIPELINE VOLTOOID")
print("Aantal kwartiermetingen:", len(data))
print("Aantal uurmetingen:", len(uurdata))
print("Energie (MWh):", round(energie_uur, 2))
print("Opgeslagen rijen:", aantal_opgeslagen)