def toon_energie(vermogen, uren):
    energie = vermogen * uren
    return energie

resultaat2 = toon_energie(12000, 6)

print("Opgeslagen resultaat:", resultaat2)

def bereken_energiekosten(vermogen_mw, uren, prijs_eur_mwh):
    energie_mwh = vermogen_mw * uren
    kosten_euro = energie_mwh * prijs_eur_mwh

    return kosten_euro


resultaat = bereken_energiekosten(10500, 8, 75)

print("Totale energiekosten:", resultaat, "euro")

def bereken_gaskosten(gasverbruik_mwh, gasprijs, co2_prijs=80):
    emissiefactor = 0.2  # ton CO2 per MWh gas

    gaskosten = gasverbruik_mwh * gasprijs
    co2_kosten = gasverbruik_mwh * emissiefactor * co2_prijs

    totale_kosten = gaskosten + co2_kosten

    return totale_kosten


resultaat2 = bereken_gaskosten(100, 40,120)

print("Totale kosten:", resultaat2, "euro")

def bereken_kosten_detail(gasverbruik, gasprijs, co2_prijs=80):
    emissiefactor = 0.2

    gaskosten = gasverbruik * gasprijs
    co2_kosten = gasverbruik * emissiefactor * co2_prijs

    totale_kosten = gaskosten + co2_kosten

    return gaskosten, co2_kosten, totale_kosten


# Roep de functie aan
gas, co2, totaal = bereken_kosten_detail(100, 40, 120)

print("Gaskosten:", gas)
print("CO2-kosten:", co2)
print("Totale kosten:", totaal)

_, co2, totaal = bereken_kosten_detail(200, 50, 100)

print("CO2-kosten:", co2)
print("Totale kosten:", totaal)