from wtforms import (
    BooleanField,
    Form,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    validators,
)

from .translator import FlaskTranslator

trans = FlaskTranslator()

error_msgs = {
    "uuid": trans.lazy_gettext("Invalid ID."),
    "num_range_min_0": trans.lazy_gettext("Number must be at least 0."),
}


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


class PlanSearchForm(Form):
    choices = [
        ("Plan-ID", trans.lazy_gettext("Plan ID")),
        ("Produktname", trans.lazy_gettext("Product name")),
    ]
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

    def get_email_string(self) -> str:
        return self.data["email"]

    def get_name_string(self) -> str:
        return self.data["name"]

    def get_password_string(self) -> str:
        return self.data["password"]

    def add_email_error(self, error: str) -> None:
        self.email.errors.append(error)


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
        return self.data["plan_id"].strip()


class CompanySearchForm(Form):
    choices = [
        ("Name", trans.lazy_gettext("Name")),
        ("Email", trans.lazy_gettext("Email")),
    ]
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


class CreateDraftForm(Form):
    prd_name = StringField()
    description = StringField()
    timeframe = StringField()
    prd_unit = StringField()
    prd_amount = StringField()
    costs_p = StringField()
    costs_r = StringField()
    costs_a = StringField()
    productive_or_public = StringField()
    action = StringField()

    def get_prd_name_string(self) -> str:
        return self.data["prd_name"]

    def get_description_string(self) -> str:
        return self.data["description"]

    def get_timeframe_string(self) -> str:
        return self.data["timeframe"]

    def get_prd_unit_string(self) -> str:
        return self.data["prd_unit"]

    def get_prd_amount_string(self) -> str:
        return self.data["prd_amount"]

    def get_costs_p_string(self) -> str:
        return self.data["costs_p"]

    def get_costs_r_string(self) -> str:
        return self.data["costs_r"]

    def get_costs_a_string(self) -> str:
        return self.data["costs_a"]

    def get_productive_or_public_string(self) -> str:
        return self.data["productive_or_public"]

    def get_action_string(self) -> str:
        return self.data["action"]


class InviteWorkerToCompanyForm(Form):
    member_id = StringField(
        validators=[
            FieldMustExist(message="Angabe erforderlich"),
        ],
        render_kw={"placeholder": "Mitglieder-ID"},
    )

    def get_worker_id(self) -> str:
        return self.data["member_id"]


class RequestCooperationForm(Form):
    plan_id = StringField()
    cooperation_id = StringField()

    def get_plan_id_string(self) -> str:
        return self.data["plan_id"]

    def get_cooperation_id_string(self) -> str:
        return self.data["cooperation_id"]


class PayMeansOfProductionForm(Form):
    plan_id = StringField(
        render_kw={"placeholder": "Plan-ID"},
        validators=[
            validators.InputRequired(),
            validators.UUID(message=error_msgs["uuid"]),
        ],
    )
    amount = IntegerField(
        render_kw={"placeholder": "Amount"},
        validators=[
            validators.InputRequired(),
            validators.NumberRange(min=0, message=error_msgs["num_range_min_0"]),
        ],
    )
    choices = [
        ("Fixed", trans.lazy_gettext("Fixed means of production")),
        (
            "Liquid",
            trans.lazy_gettext("Liquid means of production"),
        ),
    ]
    category = SelectField(choices=choices, validators=[validators.DataRequired()])

    def get_amount_field(self) -> int:
        return self.data["amount"]

    def get_plan_id_field(self) -> str:
        return self.data["plan_id"].strip()

    def get_category_field(self) -> str:
        return self.data["category"]


class AnswerCompanyWorkInviteForm(Form):
    is_accepted = BooleanField()

    def get_is_accepted_field(self) -> bool:
        return self.data["is_accepted"]
