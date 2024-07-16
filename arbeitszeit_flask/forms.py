from decimal import Decimal
from typing import Generic, TypeVar

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

T = TypeVar("T")


class WtFormField(Generic[T]):
    def __init__(self, form: Form, field_name: str) -> None:
        self._form = form
        self._field_name = field_name

    def get_value(self) -> T:
        return self._form.data[self._field_name]

    def attach_error(self, message: str) -> None:
        self._field.errors.append(message)

    def set_value(self, value: T) -> None:
        self._field.data = value

    @property
    def _field(self):
        return getattr(self._form, self._field_name)


trans = FlaskTranslator()

error_msgs = {
    "uuid": trans.lazy_gettext("Invalid ID."),
    "num_range_min_0": trans.lazy_gettext("Number must be at least 0."),
}


class FieldMustExist:
    def __init__(self, message: object) -> None:
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

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]

    def get_radio_string(self) -> str:
        return self.data["radio"]


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
        return WtFormField(form=self, field_name="email")

    @property
    def password_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="password")

    @property
    def name_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="name")


class RegisterAccountantForm(Form):
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
        return WtFormField(form=self, field_name="email")

    def password_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="password")

    def remember_field(self) -> WtFormField[bool]:
        return WtFormField(form=self, field_name="remember")


class RegisterPrivateConsumptionForm(Form):
    plan_id = StringField(
        trans.lazy_gettext("Plan ID"),
        render_kw={"placeholder": trans.lazy_gettext("Plan ID")},
        validators=[
            validators.InputRequired(),
        ],
    )
    amount = StringField(
        trans.lazy_gettext("Amount"),
        render_kw={"placeholder": trans.lazy_gettext("Amount")},
        validators=[
            validators.InputRequired(),
        ],
    )

    def amount_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="amount")

    def plan_id_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="plan_id")


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


class CreateDraftForm(Form):
    prd_name = StringField(
        validators=[
            validators.InputRequired(),
            validators.Length(max=100),
        ]
    )
    description = TextAreaField(validators=[validators.InputRequired()])
    timeframe = IntegerField(
        validators=[validators.InputRequired(), validators.NumberRange(min=1, max=365)],
        render_kw={"placeholder": trans.lazy_gettext("Days")},
    )
    prd_unit = StringField(validators=[validators.InputRequired()])
    prd_amount = IntegerField(
        validators=[validators.InputRequired(), validators.NumberRange(min=1)]
    )
    costs_p = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)],
        render_kw={"placeholder": trans.lazy_gettext("Hours")},
    )
    costs_r = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)],
        render_kw={"placeholder": trans.lazy_gettext("Hours")},
    )
    costs_a = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)],
        render_kw={"placeholder": trans.lazy_gettext("Hours")},
    )
    productive_or_public = BooleanField(
        trans.lazy_gettext("This plan is a public service")
    )

    def product_name_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="prd_name")

    def description_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="description")

    def timeframe_field(self) -> WtFormField[int]:
        return WtFormField(form=self, field_name="timeframe")

    def unit_of_distribution_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="prd_unit")

    def amount_field(self) -> WtFormField[int]:
        return WtFormField(form=self, field_name="prd_amount")

    def means_cost_field(self) -> WtFormField[Decimal]:
        return WtFormField(form=self, field_name="costs_p")

    def resource_cost_field(self) -> WtFormField[Decimal]:
        return WtFormField(form=self, field_name="costs_r")

    def labour_cost_field(self) -> WtFormField[Decimal]:
        return WtFormField(form=self, field_name="costs_a")

    def is_public_service_field(self) -> WtFormField[bool]:
        return WtFormField(form=self, field_name="productive_or_public")


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
        return WtFormField(form=self, field_name="amount")

    def plan_id_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="plan_id")

    def type_of_consumption_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="type_of_consumption")


class AnswerCompanyWorkInviteForm(Form):
    is_accepted = BooleanField()

    def get_is_accepted_field(self) -> bool:
        return self.data["is_accepted"]


class RequestCoordinationTransferForm(Form):
    candidate = StringField()
    cooperation = StringField()

    def candidate_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="candidate")

    def cooperation_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="cooperation")


class RequestEmailAddressChangeForm(Form):
    new_email = StringField(
        default="",
        validators=[
            validators.InputRequired(
                message=trans.lazy_gettext("Email address is required.")
            )
        ],
    )

    @property
    def new_email_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="new_email")


class ConfirmEmailAddressChangeForm(Form):
    is_accepted = BooleanField()

    def is_accepted_field(self) -> WtFormField[bool]:
        return WtFormField(form=self, field_name="is_accepted")
