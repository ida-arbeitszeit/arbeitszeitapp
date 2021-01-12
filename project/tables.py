from flask_table import Table, Col

class ProduktionsmittelTable(Table):
    id = Col('Kauf-Id')
    name = Col('Name')
    beschreibung = Col('Beschreibung')
    preis = Col('Preis')
    prozent_gebraucht = Col('Prozent_Gebraucht')

class KaeufeTable(Table):
    id = Col('Kauf-Id')
    name = Col('Name')
    beschreibung = Col('Beschreibung')
    preis = Col('Preis')

class ArbeiterTable1(Table):
    id = Col('Nutzer-Id')
    name = Col('Name')

class ArbeiterTable2(Table):
    id = Col('Nutzer-Id')
    name = Col('Name')
    summe_stunden = Col('Summe Stunden')

class ArbeitsstellenTable(Table):
    name = Col('Name Betrieb')
