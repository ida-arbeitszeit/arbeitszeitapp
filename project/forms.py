from wtforms import Form, SelectField, StringField


class ProductSearchForm(Form):
    choices = [("Name", "Name"), ("Beschreibung", "Beschreibung")]
    select = SelectField("Nach Produkten suchen:", choices=choices)
    search = StringField("")

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]
