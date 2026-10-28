import pandas as pd
from elia_download import haal_elia_data_op

# Download januari 2025
data = haal_elia_data_op("2025-01-01", "2025-02-01")

# Zet tijdstippen om naar UTC
tijdstippen = pd.to_datetime(data["datetime"], utc=True)

# Maak de verwachte kwartierreeks
verwacht = pd.date_range(
    start=tijdstippen.min(),
    end=tijdstippen.max(),
    freq="15min"
)

# Automatische controles
assert len(data) == 2976, "Onjuist aantal metingen"
assert data["totalload"].notna().all(), "Ontbrekende belastingwaarden"
assert not tijdstippen.duplicated().any(), "Dubbele tijdstippen"
assert len(verwacht.difference(pd.DatetimeIndex(tijdstippen))) == 0, "Ontbrekende kwartieren"

print("\nAlle kwaliteitscontroles geslaagd!")
print("Aantal metingen:", len(data))
print("Gemiddelde belasting:", round(data["totalload"].mean(), 2))