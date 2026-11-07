import duckdb

# Open rechtstreeks het opgeslagen Parquet-bestand
con = duckdb.connect()

resultaat = con.execute("""
    SELECT
        COUNT(*) AS aantal_uren,
        ROUND(SUM(energie_mwh), 2) AS totale_energie_mwh,
        COUNT(*) FILTER (
            WHERE aantal_kwartieren != 4
        ) AS onvolledige_uren
    FROM read_parquet(
        'data/elia_load_hourly_2025_01.parquet'
    )
""").fetchone()

# Haal de drie resultaten uit de tuple
aantal, energie, onvolledig = resultaat

print("Aantal uren:", aantal)
print("Totale energie (MWh):", energie)
print("Onvolledige uren:", onvolledig)

# Controleer het resultaat
assert aantal == 744, "Onjuist aantal uren"
assert onvolledig == 0, "Onvolledige uren gevonden"
assert abs(energie - 7778243.08) < 0.01, \
    "Totale energie wijkt af"

print("\nOpgeslagen dataset: GEVALIDEERD")

con.close()