# Importeer de functie uit een ander Python-bestand
from energie_berekeningen import bereken_kosten_detail

# Scenario met een gasprijs van 50 euro/MWh
# en een CO2-prijs van 100 euro/ton

gas, co2, totaal = bereken_kosten_detail(200, 50, 150)

print("Gaskosten:", gas, "euro")
print("CO2-kosten:", co2, "euro")
print("Totale kosten:", totaal, "euro")