import pandas as pd

# Eerste en laatste dag van de uurwisseling
dagen = [
    ("Zomertijd", "2025-03-30", "2025-03-31"),
    ("Wintertijd", "2025-10-26", "2025-10-27")
]

for naam, start, einde in dagen:

    tijdstippen = pd.date_range(
        start=start,
        end=einde,
        freq="15min",
        tz="Europe/Brussels",
        inclusive="left"
    )

    aantal_kwartieren = len(tijdstippen)
    aantal_uren = aantal_kwartieren / 4

    print("\n", naam)
    print("Aantal kwartieren:", aantal_kwartieren)
    print("Aantal uren:", aantal_uren)