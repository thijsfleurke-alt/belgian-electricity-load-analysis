import pandas as pd
import duckdb

# Lees de historische data
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
data["is_weekend"] = data["datetime"].dt.dayofweek >= 5

# Benchmark: belasting 24 uur eerder
data["naief_24u"] = data["belasting_mw"].shift(24)
data["naief_48u"] = data["belasting_mw"].shift(48)

# MODEL 5: hetzelfde uur vorige week
data["naief_168u"] = data["belasting_mw"].shift(168)

periodes = [
    ("2025-01-11", "2025-01-18"),
    ("2025-01-18", "2025-01-25"),
    ("2025-01-25", "2025-02-01")
]

resultaten = []
fouten_model5 = []

for nummer, (begin, einde) in enumerate(periodes, start=1):

    start = pd.Timestamp(begin, tz="Europe/Brussels")
    stop = pd.Timestamp(einde, tz="Europe/Brussels")

    train = data[data["datetime"] < start].copy()

    test = data[
        (data["datetime"] >= start) &
        (data["datetime"] < stop)
    ].copy()

    # MODEL 1: Gemiddelde per uur
    profiel1 = train.groupby("uur")["belasting_mw"].mean()

    test["model1"] = test["uur"].map(profiel1)

    # MODEL 2: Uur + werkdag/weekend
    profiel2 = (
        train.groupby(["uur", "is_weekend"])["belasting_mw"]
        .mean()
        .reset_index(name="model2")
    )

    test = test.merge(
        profiel2,
        on=["uur", "is_weekend"],
        how="left",
        validate="many_to_one"
    )

    # MODEL 3: Belasting 24 uur eerder
    test["model3"] = test["naief_24u"]

    # MODEL 4: belasting 48 uur eerder
    test["model4"] = test["naief_48u"]

    test["model5"] = test["naief_168u"]

    # Bereken de fout van model 5
    test["fout_model5"] = (test["belasting_mw"] - test["model5"])

    # Bewaar de fouten van deze testweek
    fouten_model5.append(
    test[
        [
            "datetime",
            "uur",
            "is_weekend",
            "belasting_mw",
            "model5",
            "fout_model5"
        ]
    ].copy()
    )

    # MODEL 6: Ensemble van model 2 en model 5

    test["model6"] = (0.5 * test["model2"] + 0.5 * test["model5"])


    # Controleer ontbrekende voorspellingen
    assert test[["model1", "model2", "model3", "model4", "model5"]].notna().all().all()

    # Bereken MAE voor elk model
    mae1 = (test["belasting_mw"] - test["model1"]).abs().mean()
    mae2 = (test["belasting_mw"] - test["model2"]).abs().mean()
    mae3 = (test["belasting_mw"] - test["model3"]).abs().mean()
    mae4 = (test["belasting_mw"] - test["model4"]).abs().mean()
    mae5 = (test["belasting_mw"] - test["model5"]).abs().mean()
    mae6 = (test["belasting_mw"] - test["model6"]).abs().mean()

    resultaten.append({
        "Test": nummer,
        "Model 1": mae1,
        "Model 2": mae2,
        "Model 3": mae3,
        "Model 4": mae4,
        "Model 5": mae5,
        "Model 6": mae6
    })

# Haal de kalenderdatum uit de Belgische tijdstippen
# Combineer de voorspelfouten van de drie testweken
fouten = pd.concat(fouten_model5, ignore_index=True)

# Haal de kalenderdatum uit de tijdstippen
fouten["datum"] = fouten["datetime"].dt.date

# Bereken de MAE en bias per dag
dagresultaten = (
    fouten.groupby("datum")["fout_model5"]
    .agg(
        bias_mw="mean",
        mae_mw=lambda x: x.abs().mean()
    )
)

# Rangschik van slechtst naar best voorspeld
slechtste_dagen = dagresultaten.sort_values(
    "mae_mw",
    ascending=False
)

print("\nVIJF SLECHTST VOORSPELDE DAGEN")
print(slechtste_dagen.head(5).round(2))

# Combineer alle drie de testweken
fouten = pd.concat(fouten_model5, ignore_index=True)

# Bereken de totale bias en MAE
bias = fouten["fout_model5"].mean()
mae = fouten["fout_model5"].abs().mean()

print("\nRESIDUAL ANALYSIS MODEL 5")
print("Gemiddelde bias:", round(bias, 2), "MW")
print("MAE:", round(mae, 2), "MW")

# Onderzoek werkdagen tegenover weekends
per_dagtype = fouten.groupby("is_weekend")["fout_model5"].agg(bias_mw="mean",mae_mw=lambda x: x.abs().mean())

print("\nWERKDAGEN VERSUS WEEKENDS")
print(per_dagtype.round(2))

# Onderzoek de bias per uur
bias_per_uur = fouten.groupby("uur")["fout_model5"].mean()

print("\nUur met grootste gemiddelde onderschatting:")
print(bias_per_uur.idxmax(), "uur")
print(round(bias_per_uur.max(), 2), "MW")

print("\nUur met grootste gemiddelde overschatting:")
print(bias_per_uur.idxmin(), "uur")
print(round(bias_per_uur.min(), 2), "MW")

# Vergelijk de resultaten
tabel = pd.DataFrame(resultaten)

print("\nMAE PER TESTWEEK (MW)")
print(tabel.round(2).to_string(index=False))

print("\nGEMIDDELDE MAE (MW)")
print(tabel[["Model 1", "Model 2", "Model 3", "Model 4", "Model 5", "Model 6"]].mean().round(2))

print("\nBESTE MODEL:")
print(tabel[["Model 1", "Model 2", "Model 3", "Model 4", "Model 5", "Model 6"]].mean().idxmin())

# Vergelijk dagelijkse gemiddelden met vorige week
fouten["datum"] = fouten["datetime"].dt.date
daggemiddelden = fouten.groupby("datum").agg(
    werkelijk_mw=("belasting_mw", "mean"),
    vorige_week_mw=("model5", "mean")
)

# Bereken het verschil
daggemiddelden["verschil_mw"] = (
    daggemiddelden["werkelijk_mw"]
    - daggemiddelden["vorige_week_mw"]
)

# Selecteer de drie slechtst voorspelde dagen
drie_slechtste = slechtste_dagen.head(3).index

print("\nVERGELIJKING MET VORIGE WEEK")
print(
    daggemiddelden.loc[drie_slechtste].round(2)
)

# Bereken het procentuele verschil tegenover vorige week
daggemiddelden["verandering_pct"] = (
    daggemiddelden["verschil_mw"]
    / daggemiddelden["vorige_week_mw"]
) * 100

print("\nWEKELIJKSE VERANDERING")
print(
    daggemiddelden.loc[
        drie_slechtste,
        ["verschil_mw", "verandering_pct"]
    ].round(2)
)