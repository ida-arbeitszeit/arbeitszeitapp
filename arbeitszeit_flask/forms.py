from decimal import Decimal

from wtforms import (
    BooleanField,
    DecimalField,
    Form,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
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
        trans.lazy_gettext("Search Plans"),
        choices=choices,
        validators=[validators.DataRequired()],
    )
    search = StringField(
        trans.lazy_gettext("Search term"),
        validators=[
            FieldMustExist(message=trans.lazy_gettext("Required")),
        ],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]


class RegisterForm(Form):
    email = StringField(
        trans.lazy_gettext("Email"),
        validators=[
            validators.Email(
                message=trans.lazy_gettext("Proper email address required")
            )
        ],
    )
    name = StringField(
        trans.lazy_gettext("Name"),
        validators=[validators.InputRequired(message="Name is required")],
    )
    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.Length(
                min=8,
                message=trans.lazy_gettext(
                    "The password must be at least 8 characters long"
                ),
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


class RegisterAccountantForm(Form):
    email = StringField(
        "Email",
        validators=[validators.InputRequired(message="Emailadresse erforderlich")],
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

    def get_email_address(self) -> str:
        return self.data["email"]

    def get_name(self) -> str:
        return self.data["name"]

    def get_password(self) -> str:
        return self.data["password"]


class LoginForm(Form):
    email = StringField(
        trans.lazy_gettext("Email"),
        validators=[
            validators.InputRequired(
                message=trans.lazy_gettext("Email address required")
            )
        ],
    )
    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.InputRequired(message=trans.lazy_gettext("Password is required"))
        ],
    )
    remember = BooleanField(trans.lazy_gettext("Remember login?"))


class PayConsumerProductForm(Form):
    plan_id = StringField(
        trans.lazy_gettext("Plan ID"),
        render_kw={"placeholder": trans.lazy_gettext("Plan ID")},
        validators=[validators.InputRequired()],
    )
    amount = StringField(
        trans.lazy_gettext("Amount"),
        render_kw={"placeholder": trans.lazy_gettext("Amount")},
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
        trans.lazy_gettext("Search for company"),
        choices=choices,
        validators=[validators.DataRequired()],
    )
    search = StringField(
        trans.lazy_gettext("Search term"),
        validators=[
            FieldMustExist(message=trans.lazy_gettext("Required")),
        ],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]


class CreateDraftForm(Form):
    prd_name = StringField(
        validators=[
            validators.InputRequired(),
            validators.Length(max=100),
        ]
    )
    description = TextAreaField(validators=[validators.InputRequired()])
    timeframe = IntegerField(
        validators=[validators.InputRequired(), validators.NumberRange(min=1, max=365)]
    )
    prd_unit = StringField(validators=[validators.InputRequired()])
    prd_amount = IntegerField(
        validators=[validators.InputRequired(), validators.NumberRange(min=1)]
    )
    costs_p = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)]
    )
    costs_r = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)]
    )
    costs_a = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)]
    )
    productive_or_public = RadioField(
        choices=[
            ("productive", trans.lazy_gettext("Productive")),
            (
                "public",
                trans.lazy_gettext("Public"),
            ),
        ],
        validators=[validators.InputRequired()],
    )
    action = StringField()

    def get_prd_name(self) -> str:
        return self.data["prd_name"]

    def get_description(self) -> str:
        return self.data["description"]

    def get_timeframe(self) -> int:
        return self.data["timeframe"]

    def get_prd_unit(self) -> str:
        return self.data["prd_unit"]

    def get_prd_amount(self) -> int:
        return self.data["prd_amount"]

    def get_costs_p(self) -> Decimal:
        return self.data["costs_p"]

    def get_costs_r(self) -> Decimal:
        return self.data["costs_r"]

    def get_costs_a(self) -> Decimal:
        return self.data["costs_a"]

    def get_productive_or_public(self) -> str:
        return self.data["productive_or_public"]

    def get_action(self) -> str:
        return self.data["action"]


class InviteWorkerToCompanyForm(Form):
    member_id = StringField(
        validators=[
            FieldMustExist(message=trans.lazy_gettext("Required")),
        ],
        render_kw={"placeholder": trans.lazy_gettext("Member ID")},
    )

    def get_worker_id(self) -> str:
        return self.data["member_id"]


class CreateCooperationForm(Form):
    name = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Name")},
        validators=[validators.InputRequired()],
    )
    definition = TextAreaField(
        render_kw={"placeholder": trans.lazy_gettext("Definition")},
        validators=[validators.InputRequired()],
    )

    def get_name_string(self) -> str:
        return self.data["name"]

    def get_definition_string(self) -> str:
        return self.data["definition"]


class RequestCooperationForm(Form):
    plan_id = StringField()
    cooperation_id = StringField()

    def get_plan_id_string(self) -> str:
        return self.data["plan_id"]

    def get_cooperation_id_string(self) -> str:
        return self.data["cooperation_id"]


class PayMeansOfProductionForm(Form):
    plan_id = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Plan ID")},
        validators=[
            validators.InputRequired(),
            validators.UUID(message=error_msgs["uuid"]),
        ],
    )
    amount = IntegerField(
        render_kw={"placeholder": trans.lazy_gettext("Amount")},
        validators=[
            validators.InputRequired(),
            validators.NumberRange(min=0, message=error_msgs["num_range_min_0"]),
        ],
    )
    choices = [
        ("Fixed", trans.lazy_gettext(trans.lazy_gettext("Fixed means of production"))),
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
