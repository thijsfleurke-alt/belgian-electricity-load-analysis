def bereken_kosten_detail(gasverbruik, gasprijs, co2_prijs=80):
    emissiefactor = 0.2

    gaskosten = gasverbruik * gasprijs
    co2_kosten = gasverbruik * emissiefactor * co2_prijs
    totale_kosten = gaskosten + co2_kosten

    return gaskosten, co2_kosten, totale_kosten