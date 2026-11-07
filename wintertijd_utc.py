import pandas as pd

# Tijdstippen rond de overgang naar wintertijd
tijdstippen = pd.date_range(
    start="2025-10-26 01:30",
    end="2025-10-26 03:30",
    freq="30min",
    tz="Europe/Brussels"
)

# Maak een tabel met Belgische tijd en UTC
data = pd.DataFrame({
    "Belgische_tijd": tijdstippen.strftime(
        "%Y-%m-%d %H:%M %z"
    ),
    "UTC": tijdstippen.tz_convert("UTC").strftime(
        "%Y-%m-%d %H:%M %z"
    )
})

print(data)