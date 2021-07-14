from wtforms import Form, SelectField, StringField


class ProductSearchForm(Form):
    choices = [("Name", "Name"), ("Beschreibung", "Beschreibung")]
    select = SelectField("Nach Produkten suchen:", choices=choices)
    search = StringField("")
