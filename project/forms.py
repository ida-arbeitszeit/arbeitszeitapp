from wtforms import Form, StringField, SelectField, DecimalField

class ProductSearchForm(Form):
    choices = [('Name', 'Name'),
               ('Beschreibung', 'Beschreibung')]
    select = SelectField('Nach Produkten suchen:', choices=choices)
    search = StringField('')
