from flask_table import Table, Col


class KaeufeTable(Table):
    id = Col("Kauf-Id")
    name = Col("Name")
    beschreibung = Col("Beschreibung")
    preis = Col("Preis")


class WorkersTable(Table):
    id = Col("Mitglieder-Id")
    name = Col("Name")
