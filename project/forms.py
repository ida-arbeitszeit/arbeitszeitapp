from wtforms import (
    BooleanField,
    Form,
    PasswordField,
    SelectField,
    StringField,
    validators,
)


class FieldMustExist:
    def __init__(self, message: str) -> None:
        self.message = message

    def __call__(self, form, field):
        if not self._field_has_data(field):
            if self.message is None:
                message = field.gettext("This field is required.")
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)

    def _field_has_data(self, field):
        return field.raw_data


class ProductSearchForm(Form):
    choices = [("Name", "Name"), ("Beschreibung", "Beschreibung")]
    select = SelectField(
        "Nach Produkten suchen", choices=choices, validators=[validators.DataRequired()]
    )
    search = StringField(
        "Suchbegriff",
        validators=[
            FieldMustExist(message="Angabe erforderlich"),
        ],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]


class PlanSearchForm(Form):
    choices = [("Plan-ID", "Plan-ID"), ("Produktname", "Produktname")]
    select = SelectField(
        "Nach Plänen suchen", choices=choices, validators=[validators.DataRequired()]
    )
    search = StringField(
        "Suchbegriff",
        validators=[
            FieldMustExist(message="Angabe erforderlich"),
        ],
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


class PayConsumerProductForm(Form):
    plan_id = StringField(
        "Plan-ID",
        render_kw={"placeholder": "Plan-ID"},
        validators=[validators.InputRequired()],
    )
    amount = StringField(
        "Menge",
        render_kw={"placeholder": "Menge"},
        validators=[validators.InputRequired()],
    )

    def get_amount_field(self) -> str:
        return self.data["amount"]

    def get_plan_id_field(self) -> str:
        return self.data["plan_id"]


class CompanySearchForm(Form):
    choices = [("Name", "Name"), ("Email", "Email")]
    select = SelectField(
        "Nach Betrieb suchen", choices=choices, validators=[validators.DataRequired()]
    )
    search = StringField(
        "Suchbegriff",
        validators=[
            FieldMustExist(message="Angabe erforderlich"),
        ],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]
