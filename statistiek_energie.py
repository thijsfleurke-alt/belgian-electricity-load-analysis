import duckdb

# Lees de uurdata van januari 2025
data = duckdb.sql("""
    SELECT belasting_mw
    FROM read_parquet(
        'data/elia_load_hourly_2025_01.parquet'
    )
""").df()

belasting = data["belasting_mw"]

# Beschrijvende statistieken
gemiddelde = belasting.mean()
mediaan = belasting.median()
standaardafwijking = belasting.std()
p10 = belasting.quantile(0.10)
p90 = belasting.quantile(0.90)

# Relatieve spreiding
variatiecoefficient = (
    standaardafwijking / gemiddelde
) * 100

print("Gemiddelde MW:", round(gemiddelde, 2))
print("Mediaan MW:", round(mediaan, 2))
print("Standaardafwijking MW:", round(standaardafwijking, 2))
print("10e percentiel MW:", round(p10, 2))
print("90e percentiel MW:", round(p90, 2))
print("Variatiecoefficient:", round(variatiecoefficient, 2), "%")