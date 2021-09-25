from wtforms import (
    BooleanField,
    Form,
    PasswordField,
    SelectField,
    StringField,
    validators,
)


class ProductSearchForm(Form):
    choices = [("Name", "Name"), ("Beschreibung", "Beschreibung")]
    select = SelectField(
        "Nach Produkten suchen", choices=choices, validators=[validators.DataRequired()]
    )
    search = StringField(
        "Suchbegriff",
        validators=[validators.InputRequired(message="Suchbegriff erforderlich")],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]


class RegisterForm(Form):
    email = StringField(
        "Email",
        validators=[validators.Email(message="Korrekte Emailadresse erforderlich")],
    )
    name = StringField(
        "Name",
        validators=[validators.InputRequired(message="Name ist erforderlich")],
    )
    password = PasswordField(
        "Passwort",
        validators=[
            validators.Length(
                min=8, message="Passwort muss mindestens 8 Zeichen umfassen"
            )
        ],
    )


class LoginForm(Form):
    email = StringField(
        "Email",
        validators=[validators.InputRequired(message="Emailadresse erforderlich")],
    )
    password = PasswordField(
        "Passwort",
        validators=[validators.InputRequired(message="Passwort erforderlich")],
    )
    remember = BooleanField("Angemeldet bleiben?")
