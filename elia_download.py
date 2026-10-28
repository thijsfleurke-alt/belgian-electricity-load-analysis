import requests
import pandas as pd


def haal_elia_data_op(startdatum, einddatum):

    url = (
        "https://opendata.elia.be/api/explore/v2.1/"
        "catalog/datasets/ods001/records"
    )

    parameters = {
        "limit": 100,
        "where": (
            f"datetime >= '{startdatum}' "
            f"AND datetime < '{einddatum}'"
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

        totaal = gegevens["total_count"]

        print("Opgehaald:", len(alle_metingen), "van", totaal)

        if len(alle_metingen) >= totaal:
            break

        if len(pagina) == 0:
            raise RuntimeError("Download onvolledig: lege pagina")

        offset = offset + len(pagina)

    data = pd.DataFrame(alle_metingen)

    if len(data) != totaal:
        raise RuntimeError("Aantal metingen komt niet overeen")

    return data