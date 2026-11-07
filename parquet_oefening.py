from pathlib import Path
import pandas as pd
import duckdb

from elia_download import haal_elia_data_op

# Download januari 2025
data = haal_elia_data_op("2025-01-01", "2025-02-01")

# Zet datetime om naar een echt tijdstip in UTC
data["datetime"] = pd.to_datetime(data["datetime"], utc=True)

print("\nDatatypes:")
print(data[["datetime", "totalload"]].dtypes)

# Maak een map voor de bestanden
Path("data").mkdir(exist_ok=True)

# Registreer het DataFrame in DuckDB
con = duckdb.connect()
con.register("metingen", data)

# Schrijf twee kolommen naar Parquet
con.execute("""
    COPY (
        SELECT datetime, totalload
        FROM metingen
    )
    TO 'data/elia_load_2025_01.parquet'
    (FORMAT PARQUET)
""")

# Lees het bestand opnieuw in via DuckDB
aantal = con.execute("""
    SELECT COUNT(*)
    FROM read_parquet('data/elia_load_2025_01.parquet')
""").fetchone()[0]

print("\nAantal metingen in Parquet:", aantal)

con.close()