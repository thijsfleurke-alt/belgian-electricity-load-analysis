import requests
import pandas as pd

url = (
    "https://opendata.elia.be/api/explore/v2.1/"
    "catalog/datasets/ods001/records"
)

parameters = {
    "limit": 100,
    "where": (
        "datetime >= '2025-01-01' "
        "AND datetime < '2025-01-03'"
    ),
    "timezone": "Europe/Brussels",
    "order_by": "datetime ASC"
}

alle_metingen = []
offset = 0

while True:

    parameters["offset"] = offset

    response = requests.get(
        url,
        params=parameters,
        timeout=20
    )

    response.raise_for_status()
    gegevens = response.json()

    pagina = gegevens["results"]

    alle_metingen.extend(pagina)

    print("Offset:", offset)
    print("Ontvangen:", len(pagina))

    # Controleer of alle metingen binnen zijn
    if len(alle_metingen) >= gegevens["total_count"]:
        break

    # Stop ook bij een onverwacht lege pagina
    if len(pagina) == 0:
        raise RuntimeError("Geen metingen ontvangen terwijl er nog ontbreken")

    # Ga naar de volgende pagina
    offset = offset + len(pagina)

data = pd.DataFrame(alle_metingen)

print("Totaal opgehaald:", len(data))
print("Totaal volgens API:", gegevens["total_count"])