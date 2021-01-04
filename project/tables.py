from flask_table import Table, Col

class Results(Table):
    id = Col('Id', show=False)
    name = Col('Name')
    betrieb = Col('Betrieb')
    beschreibung = Col('Beschreibung')
    preis = Col('Preis')

class ProduktionsmittelTable(Table):
    id = Col('Kauf-Id')
    name = Col('Name')
    beschreibung = Col('Beschreibung')
    preis = Col('Preis')
    prozent_gebraucht = Col('Prozent_Gebraucht')

# class ProduktionsmittelTable2(Table):
#     id = Col('Kauf-Id')
#     name = Col('Name')
#     beschreibung = Col('Beschreibung')
#     preis = Col('Preis')
#     prozent_gebraucht = Col('Prozent_Gebraucht')
#     nutzen = Col('Nutzen')
#     prozent = Col('Prozent')
