from pathlib import Path
import duckdb

# Bestandslocaties
parquet = Path("data/elia_load_2025_01.parquet")
csv = Path("data/elia_load_2025_01.csv")

# Open DuckDB
con = duckdb.connect()

# Zet hetzelfde Parquet-bestand om naar CSV
con.execute("""
    COPY (
        SELECT *
        FROM read_parquet('data/elia_load_2025_01.parquet')
    )
    TO 'data/elia_load_2025_01.csv'
    (FORMAT CSV, HEADER TRUE)
""")

# Bereken bestandsgrootte in kilobytes
parquet_kb = parquet.stat().st_size / 1024
csv_kb = csv.stat().st_size / 1024

# Bereken hoeveel ruimte Parquet bespaart
besparing = (1 - parquet_kb / csv_kb) * 100

print("CSV-grootte:", round(csv_kb, 2), "KB")
print("Parquet-grootte:", round(parquet_kb, 2), "KB")
print("Ruimtebesparing:", round(besparing, 1), "%")

con.close()