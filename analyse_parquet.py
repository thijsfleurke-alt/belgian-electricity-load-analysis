import duckdb

con = duckdb.connect()

# Analyseer rechtstreeks het Parquet-bestand
resultaat = con.execute("""
    SELECT
        CAST(
            datetime AT TIME ZONE 'Europe/Brussels'
            AS DATE
        ) AS datum,

        ROUND(AVG(totalload), 2) AS gemiddelde_mw

    FROM read_parquet('data/elia_load_2025_01.parquet')

    GROUP BY datum
    ORDER BY gemiddelde_mw DESC
    LIMIT 3

""").df()

print(resultaat)

con.close()