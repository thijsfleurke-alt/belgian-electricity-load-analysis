import pandas as pd
import matplotlib.pyplot as plt

# Lees de Elia-dataset
data = pd.read_csv(
    "elia_2025.csv",
    sep=None,
    engine="python"
)

data.columns = data.columns.str.replace("\ufeff", "", regex=False)

# Toon de eerste vijf rijen
print("Eerste vijf metingen:")
print(data.head())

# Hoeveel metingen zijn er?
print("Aantal metingen:", len(data))

# Welke kolommen bevat de dataset?
print("Kolomnamen:")
print(data.columns.tolist())

print("Eerste kolom:", repr(data.columns[0]))


# Zet tekst om naar echte datum- en tijdwaarden
data["Datetime"] = pd.to_datetime(
    data["Datetime"],
    utc=True
).dt.tz_convert("Europe/Brussels")

# Sorteer de metingen chronologisch
data = data.sort_values("Datetime")

# Bereken statistieken
gemiddelde = data["Total Load"].mean()
minimum = data["Total Load"].min()
maximum = data["Total Load"].max()

# Toon de resultaten
print("\n--- Belgische elektriciteitsvraag januari 2025 ---")
print("Gemiddelde belasting:", round(gemiddelde, 2), "MW")
print("Minimale belasting:", minimum, "MW")
print("Maximale belasting:", maximum, "MW")

# Controleer de eerste en laatste meting
print("\nEerste meting:")
print(data[["Datetime", "Total Load"]].head(1))

print("\nLaatste meting:")
print(data[["Datetime", "Total Load"]].tail(1))

# Maak de rijnummers opnieuw opeenvolgend
data = data.reset_index(drop=True)

# Genereer alle verwachte kwartiermetingen
verwachte_tijden = pd.date_range(
    start="2025-01-01",
    end="2025-02-01",
    freq="15min",
    tz="Europe/Brussels",
    inclusive="left"
)

# Haal de werkelijk gemeten tijdstippen op
gemeten_tijden = pd.DatetimeIndex(data["Datetime"])

# Controleer de datakwaliteit
duplicaten = data["Datetime"].duplicated().sum()

ontbrekende_tijden = verwachte_tijden.difference(gemeten_tijden)

ontbrekende_waarden = data["Total Load"].isna().sum()

print("\n--- DATAKWALITEIT ---")
print("Verwachte metingen:", len(verwachte_tijden))
print("Werkelijke metingen:", len(data))
print("Dubbele tijdstippen:", duplicaten)
print("Ontbrekende tijdstippen:", len(ontbrekende_tijden))
print("Ontbrekende meetwaarden:", ontbrekende_waarden)


# Maak een grafiek van de elektriciteitsvraag
plt.figure(figsize=(12, 5))

# Teken de 2976 kwartiermetingen
plt.plot(
    data["Datetime"],
    data["Total Load"],
    color="blue",
    linewidth=0.8
)

# Titels en assen
plt.title("Belgische elektriciteitsvraag - januari 2025")
plt.xlabel("Datum")
plt.ylabel("Elektriciteitsbelasting (MW)")

# Raster toevoegen
plt.grid(True)

# Datums leesbaar maken
plt.xticks(rotation=45)
plt.tight_layout()

# Grafiek opslaan
plt.savefig("elia_januari_2025.png", dpi=150)

# Grafiek tonen
plt.show()


# Haal het uur uit ieder tijdstip
data["uur"] = data["Datetime"].dt.hour

# Bereken de gemiddelde belasting per uur
dagprofiel = data.groupby("uur")["Total Load"].mean()

# Toon de resultaten
print("\n--- GEMIDDELD DAGPROFIEL ---")
print(dagprofiel)

# Zoek het uur met de hoogste en laagste belasting
piek_uur = dagprofiel.idxmax()
dal_uur = dagprofiel.idxmin()

print("Hoogste gemiddelde belasting om:", piek_uur, "uur")
print("Laagste gemiddelde belasting om:", dal_uur, "uur")

# Nieuwe figuur maken
plt.figure(figsize=(10, 5))

# Gemiddelde belasting per uur tekenen
plt.plot(
    dagprofiel.index,
    dagprofiel.values,
    marker="o",
    color="blue"
)

plt.title("Gemiddeld dagprofiel - België, januari 2025")
plt.xlabel("Uur van de dag")
plt.ylabel("Gemiddelde belasting (MW)")

plt.xticks(range(24))
plt.grid(True)
plt.tight_layout()

plt.savefig("elia_dagprofiel_2025.png", dpi=150)
plt.show()

# Bepaal de dag van de week
data["weekdag"] = data["Datetime"].dt.dayofweek

# Maak een nieuwe kolom voor weekends
data["is_weekend"] = data["weekdag"] >= 5

# Bereken de gemiddelde belasting
gemiddelde_werkdag = data.loc[
    ~data["is_weekend"], "Total Load"
].mean()

gemiddelde_weekend = data.loc[
    data["is_weekend"], "Total Load"
].mean()

print("\n--- WERKDAGEN VS WEEKENDS ---")
print("Gemiddelde werkdag:", round(gemiddelde_werkdag, 2), "MW")
print("Gemiddelde weekend:", round(gemiddelde_weekend, 2), "MW")

verschil = gemiddelde_werkdag - gemiddelde_weekend

print("Verschil:", round(verschil, 2), "MW")

# Groepeer per uur en type dag
profielen = data.groupby(
    ["is_weekend", "uur"]
)["Total Load"].mean().unstack(level=0)

# Maak de grafiek
plt.figure(figsize=(10, 5))

plt.plot(
    profielen.index,
    profielen[False],
    label="Werkdagen",
    marker="o"
)

plt.plot(
    profielen.index,
    profielen[True],
    label="Weekends",
    marker="s"
)

plt.title("Belgische elektriciteitsvraag: werkdagen vs weekends")
plt.xlabel("Uur van de dag")
plt.ylabel("Gemiddelde belasting (MW)")

plt.xticks(range(24))
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("elia_werkdagen_weekends.png", dpi=150)
plt.show()


# Bereken het procentuele verschil
verschil_procent = (
    gemiddelde_weekend - gemiddelde_werkdag
) / gemiddelde_werkdag * 100

print(
    "Verschil weekend t.o.v. werkdag:",
    round(verschil_procent, 2),
    "%"
)

# Bereken de gemiddelde dagelijkse energie
energie_werkdag = gemiddelde_werkdag * 24
energie_weekend = gemiddelde_weekend * 24

print("Gemiddelde energie werkdag:", round(energie_werkdag), "MWh")
print("Gemiddelde energie weekend:", round(energie_weekend), "MWh")


# Bereken het absolute verschil per uur
profielen["verschil_MW"] = (
    profielen[True] - profielen[False]
)

# Bereken het procentuele verschil per uur
profielen["verschil_pct"] = (
    profielen["verschil_MW"] / profielen[False] * 100
)

# Toon de resultaten
print("\n--- VERSCHIL PER UUR ---")
print(profielen[["verschil_MW", "verschil_pct"]].round(2))

plt.figure(figsize=(10, 5))

plt.bar(
    profielen.index,
    profielen["verschil_pct"],
    color="steelblue"
)

plt.axhline(0, color="black", linewidth=0.8)

plt.title("Verschil elektriciteitsvraag weekend vs werkdag")
plt.xlabel("Uur van de dag")
plt.ylabel("Verschil (%)")

plt.xticks(range(24))
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("elia_weekendverschil_per_uur.png", dpi=150)
plt.show()

# Zoek het uur met het grootste negatieve verschil
grootste_verschil_uur = profielen["verschil_pct"].idxmin()

# Zoek het bijbehorende percentage
grootste_verschil_pct = profielen["verschil_pct"].min()

print("\n--- GROOTSTE WEEKENDVERSCHIL ---")

print("Uur:", grootste_verschil_uur)

print(
    "Procentueel verschil:",
    round(grootste_verschil_pct, 2),
    "%"
)