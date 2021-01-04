from wtforms import Form, StringField, SelectField, DecimalField

class ProductSearchForm(Form):
    choices = [('Name', 'Name'),
               ('Beschreibung', 'Beschreibung')]
    select = SelectField('Nach Produkten suchen:', choices=choices)
    search = StringField('')

class ProductForm(Form):
    name = StringField('Name')
    betrieb = StringField('Betrieb')
    beschreibung = StringField('Beschreibung')
    # prod_mittel = DecimalField('Produktionsmittel')
    arbeit = DecimalField("Arbeit")
