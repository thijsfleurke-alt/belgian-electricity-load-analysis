import pandas as pd


def controleer_energiedata(data):

    # Zet tijdstippen om naar UTC
    tijdstippen = pd.to_datetime(
        data["datetime"], utc=True
    )

    # Controleer ontbrekende waarden
    ontbrekende_belasting = data["belasting_mw"].isna().sum()
    ontbrekende_prijzen = data["prijs_eur_mwh"].isna().sum()

    # Controleer dubbele tijdstippen
    duplicaten = tijdstippen.duplicated().sum()

    # Controleer ontbrekende uren
    verwacht = pd.date_range(
        start=tijdstippen.min(),
        end=tijdstippen.max(),
        freq="1h"
    )

    ontbrekende_uren = len(
        verwacht.difference(
            pd.DatetimeIndex(tijdstippen.dropna())
        )
    )

    # Bereken de prijsdekking
    prijsdekking = (
        data["prijs_eur_mwh"].notna().sum()
        / len(data)
    ) * 100

    # Toon de resultaten
    print("\nAUTOMATISCHE DATAKWALITEIT")
    print("Ontbrekende belasting:", ontbrekende_belasting)
    print("Dubbele tijdstippen:", duplicaten)
    print("Ontbrekende uren:", ontbrekende_uren)
    print("Ontbrekende prijzen:", ontbrekende_prijzen)
    print("Prijsdekking:", round(prijsdekking, 2), "%")

    # Stop wanneer de basisgegevens niet betrouwbaar zijn
    assert tijdstippen.notna().all(), "Ongeldige tijdstippen"
    assert ontbrekende_belasting == 0, "Ontbrekende belasting"
    assert duplicaten == 0, "Dubbele tijdstippen"
    assert ontbrekende_uren == 0, "Ontbrekende uren"

    print("\nKwaliteitscontrole belasting: GESLAAGD")
    

def controleer_uurbelasting(data):

    if data.empty:
        raise ValueError("De dataset is leeg")

    tijd = pd.to_datetime(data["datetime"], utc=True)

    assert tijd.notna().all(), "Ongeldige tijdstippen"

    assert data["belasting_mw"].notna().all(), \
        "Ontbrekende belastingwaarden"

    assert not tijd.duplicated().any(), \
        "Dubbele tijdstippen"

    verwacht = pd.date_range(
        start=tijd.min(),
        end=tijd.max(),
        freq="1h"
    )

    ontbrekende = verwacht.difference(
        pd.DatetimeIndex(tijd)
    )

    assert len(ontbrekende) == 0, \
        "Ontbrekende uren"

    assert (data["aantal_kwartieren"] == 4).all(), \
        "Onvolledige uren"

    print("Kwaliteitscontrole uurbelasting: GESLAAGD")