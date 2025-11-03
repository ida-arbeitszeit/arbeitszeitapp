from typing import Generic, Self, TypeVar

from wtforms import (
    BooleanField,
    Field,
    Form,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    ValidationError,
    validators,
)

from .translator import FlaskTranslator

T = TypeVar("T")


class WtFormField(Generic[T]):
    def __init__(self, field: Field) -> None:
        self._field = field

    def get_value(self) -> T:
        return self._field.data

    def attach_error(self, message: str) -> None:
        self._field.errors.append(message)

    def set_value(self, value: T) -> None:
        self._field.data = value


trans = FlaskTranslator()

error_msgs = {
    "uuid": trans.lazy_gettext("Invalid ID."),
    "num_range_min_0": trans.lazy_gettext("Number must be at least 0."),
}


class PlanSearchForm(Form):
    choices = [
        ("Plan-ID", trans.lazy_gettext("Plan ID")),
        ("Produktname", trans.lazy_gettext("Product name")),
    ]
    select = SelectField(
        trans.lazy_gettext("Search Plans"),
        choices=choices,
        validators=[validators.DataRequired()],
        default="Produktname",
    )
    search = StringField(
        trans.lazy_gettext("Search term"),
        default="",
    )

    choices_radio = [
        ("activation", trans.lazy_gettext("Newest")),
        ("company_name", trans.lazy_gettext("Company name")),
    ]
    radio = RadioField(
        choices=choices_radio,
        default="activation",
    )

    include_expired_plans = BooleanField(
        trans.lazy_gettext("Search also for expired plans"),
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]

    def get_radio_string(self) -> str:
        return self.data["radio"]

    def get_checkbox_value(self) -> bool:
        return self.data["include_expired_plans"]


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
        validators=[
            validators.InputRequired(message=trans.lazy_gettext("Name is required"))
        ],
    )
    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.Length(
                min=8,
                message=trans.lazy_gettext(
                    "The password must be at least 8 characters in length"
                ),
            ),
            validators.EqualTo(
                "repeat_password", message=trans.lazy_gettext("Passwords must match")
            ),
        ],
    )
    repeat_password = PasswordField(trans.lazy_gettext("Repeat Password"))

    @property
    def email_field(self) -> WtFormField[str]:
        return WtFormField(self.email)

    @property
    def password_field(self) -> WtFormField[str]:
        return WtFormField(self.password)

    @property
    def name_field(self) -> WtFormField[str]:
        return WtFormField(self.name)


class RegisterAccountantForm(Form):
    extracted_token: str
    email = StringField(
        trans.lazy_gettext("Email"),
        validators=[
            validators.InputRequired(
                message=trans.lazy_gettext("Email address is required")
            )
        ],
    )
    name = StringField(
        trans.lazy_gettext("Name"),
        validators=[
            validators.InputRequired(message=trans.lazy_gettext("Name is required"))
        ],
    )
    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.Length(
                min=8,
                message=trans.lazy_gettext(
                    "The password must be at least 8 characters in length"
                ),
            )
        ],
    )

    def validate_email(form: Self, field: StringField) -> None:
        input_email = field.data.casefold().strip() if field.data else ""
        token_email = form.extracted_token.casefold().strip()
        if input_email != token_email:
            raise ValidationError(
                message=str(
                    trans.lazy_gettext(
                        "The entered email is not the one the invitation was sent to"
                    )
                )
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

    def email_field(self) -> WtFormField[str]:
        return WtFormField(self.email)

    def password_field(self) -> WtFormField[str]:
        return WtFormField(self.password)

    def remember_field(self) -> WtFormField[bool]:
        return WtFormField(self.remember)


class CompanySearchForm(Form):
    choices = [
        ("Name", trans.lazy_gettext("Name")),
        ("Email", trans.lazy_gettext("Email")),
    ]
    select = SelectField(
        trans.lazy_gettext("Search for company"),
        choices=choices,
        default="Name",
    )
    search = StringField(
        trans.lazy_gettext("Search term"),
        default="",
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]


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


class RegisterProductiveConsumptionForm(Form):
    plan_id = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Plan ID")},
        validators=[
            validators.InputRequired(),
        ],
    )
    amount = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Amount")},
        validators=[
            validators.InputRequired(),
        ],
    )
    choices = [
        ("", ""),
        ("fixed", trans.lazy_gettext("Fixed means of production")),
        (
            "liquid",
            trans.lazy_gettext("Liquid means of production"),
        ),
    ]
    type_of_consumption = SelectField(
        trans.lazy_gettext("Type of consumption"),
        choices=choices,
        validators=[validators.DataRequired()],
    )

    def amount_field(self) -> WtFormField[str]:
        return WtFormField(self.amount)

    def plan_id_field(self) -> WtFormField[str]:
        return WtFormField(self.plan_id)

    def type_of_consumption_field(self) -> WtFormField[str]:
        return WtFormField(self.type_of_consumption)


class AnswerCompanyWorkInviteForm(Form):
    is_accepted = BooleanField()

    def get_is_accepted_field(self) -> bool:
        return self.data["is_accepted"]


class RequestCoordinationTransferForm(Form):
    candidate = StringField()
    cooperation = StringField()

    def candidate_field(self) -> WtFormField[str]:
        return WtFormField(self.candidate)

    def cooperation_field(self) -> WtFormField[str]:
        return WtFormField(self.cooperation)


class RequestEmailAddressChangeForm(Form):
    new_email = StringField(
        label=trans.lazy_gettext("New email address"),
        validators=[
            validators.InputRequired(
                message=trans.lazy_gettext("Email address is required.")
            )
        ],
    )

    current_password = PasswordField(
        label=trans.lazy_gettext("Current password"),
        validators=[
            validators.InputRequired(message=trans.lazy_gettext("Password is required"))
        ],
    )

    @property
    def new_email_field(self) -> WtFormField[str]:
        return WtFormField(self.new_email)

    @property
    def current_password_field(self) -> WtFormField[str]:
        return WtFormField(self.current_password)


class ConfirmEmailAddressChangeForm(Form):
    is_accepted = BooleanField()

    def is_accepted_field(self) -> WtFormField[bool]:
        return WtFormField(self.is_accepted)
