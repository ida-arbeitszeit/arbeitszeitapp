from flask_table import Table, Col


class ProduktionsmittelTable(Table):
    id = Col('Kauf-Id')
    name = Col('Name')
    beschreibung = Col('Beschreibung')
    kaufpreis = Col('Kaufpreis')
    prozent_gebraucht = Col('Prozent Gebraucht')


class Preiszusammensetzung(Table):
    angebot1 = Col("angebot1")
    name1 = Col("name1")
    p1 = Col("p1")
    v1 = Col("v1")
    preis1 = Col("preis1")
    proz_gebr2 = Col("proz_gebr2")
    kauf2 = Col("kauf2")

    angebot2 = Col("angebot2")
    name2 = Col("name2")
    preis2 = Col("preis2")
    kosten2 = Col("kosten2")
    proz_gebr3 = Col("proz_gebr3")
    kauf3 = Col("kauf3")

    angebot3 = Col("angebot3")
    name3 = Col("name3")
    preis3 = Col("preis3")
    kosten3 = Col("kosten3")
    proz_gebr4 = Col("proz_gebr4")
    kauf4 = Col("kauf4")

    angebot4 = Col("angebot4")
    name4 = Col("name4")
    preis4 = Col("preis4")
    kosten4 = Col("kosten4")
    proz_gebr5 = Col("proz_gebr5")
    kauf5 = Col("kauf5")

    angebot5 = Col("angebot5")
    name5 = Col("name5")
    preis5 = Col("preis5")
    kosten5 = Col("kosten5")
    proz_gebr6 = Col("proz_gebr6")
    kauf6 = Col("kauf6")


class KaeufeTable(Table):
    id = Col('Kauf-Id')
    name = Col('Name')
    beschreibung = Col('Beschreibung')
    preis = Col('Preis')


class WorkersTable(Table):
    id = Col('Mitglieder-Id')
    name = Col('Name')


class HoursTable(Table):
    id = Col('Mitglieder-Id')
    name = Col('Name')
    summe_stunden = Col('Arbeitsstunden')
