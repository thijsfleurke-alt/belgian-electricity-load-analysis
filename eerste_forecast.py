import pandas as pd
import duckdb
import numpy as np

# 1. Lees de historische Elia-data
data = duckdb.sql("""
    SELECT datetime, belasting_mw
    FROM read_parquet(
        'data/elia_load_hourly_2025_01.parquet'
    )
    ORDER BY datetime
""").df()

data["datetime"] = pd.to_datetime(
    data["datetime"], utc=True
).dt.tz_convert("Europe/Brussels")

data["uur"] = data["datetime"].dt.hour

# 2. Splits chronologisch
grens = pd.Timestamp(
    "2025-01-22",
    tz="Europe/Brussels"
)

train = data[data["datetime"] < grens].copy()
test = data[data["datetime"] >= grens].copy()

print("Trainingsuren:", len(train))
print("Testuren:", len(test))

# 3. Leer het gemiddelde belastingprofiel
uurprofiel = train.groupby("uur")["belasting_mw"].mean()

# 4. Maak voorspellingen voor de testperiode
test["voorspelling_mw"] = test["uur"].map(uurprofiel)

# 5. Bereken de voorspellingsfouten
fout = test["belasting_mw"] - test["voorspelling_mw"]

mae = fout.abs().mean()
rmse = np.sqrt((fout ** 2).mean())

print("\nRESULTATEN EERSTE FORECAST")
print("MAE:", round(mae, 2), "MW")
print("RMSE:", round(rmse, 2), "MW")

print("\nEerste vijf voorspellingen:")
print(
    test[
        ["datetime", "belasting_mw", "voorspelling_mw"]
    ].head().to_string(index=False)
)

# MODEL 2: Uur + werkdag/weekend

# 0 = maandag, 6 = zondag
train["is_weekend"] = train["datetime"].dt.dayofweek >= 5
test["is_weekend"] = test["datetime"].dt.dayofweek >= 5

# Leer aparte uurprofielen voor werkdagen en weekends
profiel_week = (
    train.groupby(["uur", "is_weekend"])["belasting_mw"]
    .mean()
    .reset_index(name="voorspelling_week_mw")
)

# Koppel de juiste voorspelling aan ieder testuur
test = test.merge(
    profiel_week,
    on=["uur", "is_weekend"],
    how="left",
    validate="many_to_one"
)

# Controleer of ieder testuur een voorspelling kreeg
assert test["voorspelling_week_mw"].notna().all()

# Bereken de fouten van model 2
fout_week = (
    test["belasting_mw"] - test["voorspelling_week_mw"]
)

mae_week = fout_week.abs().mean()
rmse_week = np.sqrt((fout_week ** 2).mean())

print("\nVERGELIJKING FORECASTMODELLEN")
print("Model 1 - MAE:", round(mae, 2), "MW")
print("Model 2 - MAE:", round(mae_week, 2), "MW")
print("Model 1 - RMSE:", round(rmse, 2), "MW")
print("Model 2 - RMSE:", round(rmse_week, 2), "MW")

# Bereken de procentuele verbetering
verbetering = (1 - mae_week / mae) * 100

print("Verbetering MAE:", round(verbetering, 2), "%")

# MODEL 3: Naïeve voorspelling met 24 uur vertraging

# Sorteer de volledige tijdreeks chronologisch
historiek = data.sort_values("datetime").copy()

# Gebruik de belasting van 24 uur eerder
historiek["voorspelling_naief_mw"] = (
    historiek["belasting_mw"].shift(24)
)

# Beoordeel alleen dezelfde testperiode
test_naief = historiek[
    historiek["datetime"] >= grens
].copy()

# Controleer of alle voorspellingen beschikbaar zijn
assert test_naief["voorspelling_naief_mw"].notna().all()

# Bereken de voorspellingsfouten
fout_naief = (
    test_naief["belasting_mw"]
    - test_naief["voorspelling_naief_mw"]
)

mae_naief = fout_naief.abs().mean()
rmse_naief = np.sqrt((fout_naief ** 2).mean())

print("\nVERGELIJKING DRIE MODELLEN")

print("Model 1 - MAE:", round(mae, 2), "MW")
print("Model 2 - MAE:", round(mae_week, 2), "MW")
print("Model 3 - MAE:", round(mae_naief, 2), "MW")

print("\nModel 1 - RMSE:", round(rmse, 2), "MW")
print("Model 2 - RMSE:", round(rmse_week, 2), "MW")
print("Model 3 - RMSE:", round(rmse_naief, 2), "MW")