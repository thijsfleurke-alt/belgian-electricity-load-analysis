import requests
import pandas as pd

# Adres van de Elia API
url = (
    "https://opendata.elia.be/api/explore/v2.1/"
    "catalog/datasets/ods001/records"
)

# Vraag slechts 3 metingen op
parameters = {
    "limit": 96,
    "where": (
        "datetime >= '2025-01-01' "
        "AND datetime < '2025-01-02'"
    ),
    "timezone": "Europe/Brussels",
    "order_by": "datetime ASC"
}

try:
    response = requests.get(
        url,
        params=parameters,
        timeout=15
    )

    print("HTTP-status:", response.status_code)

    response.raise_for_status()

    # Zet het antwoord om naar Python-gegevens
    gegevens = response.json()

    print("Aantal ontvangen metingen:", len(gegevens["results"]))
    print("Totaal aantal passende metingen:", gegevens["total_count"])
    print("Eerste meting:", gegevens["results"][0])

        # Haal de metingen uit het JSON-antwoord
    metingen = gegevens["results"]

    # Zet de metingen om naar een pandas DataFrame
    data = pd.DataFrame(metingen)
        # Controleer of alle metingen zijn opgehaald
    print("Aantal rijen in DataFrame:", len(data))

    # Toon de eerste meting
    print("\nEerste meting:")
    print(data[["datetime", "totalload"]].head(1))

    # Toon de laatste meting
    print("\nLaatste meting:")
    print(data[["datetime", "totalload"]].tail(1))

    # Toon alleen het tijdstip en de elektriciteitsbelasting
    print(data[["datetime", "totalload"]].head())

except requests.exceptions.RequestException as fout:
    print("API-aanvraag mislukt:", fout)