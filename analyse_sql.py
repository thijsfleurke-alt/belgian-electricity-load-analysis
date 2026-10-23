import duckdb

resultaat = duckdb.sql("""
    WITH gecombineerde_data AS (
        SELECT
            p.uur,
            p.werkdag_MW,
            t.prijs_eur_MWh

        FROM read_csv_auto('elia_weekendprofiel_sql.csv') AS p

        LEFT JOIN (
            VALUES
                (7, 100),
                (8, 120),
                (9, 90),
                (18, 140)
        ) AS t(uur, prijs_eur_MWh)

        ON p.uur = t.uur
    )

        SELECT
            uur,
            werkdag_MW,
            prijs_eur_MWh
        FROM gecombineerde_data
        
        WHERE
            prijs_eur_MWh IS NOT NULL
            AND werkdag_MW > 11500

        ORDER BY uur
        
    
""")

print(resultaat.df().to_string(index=False))