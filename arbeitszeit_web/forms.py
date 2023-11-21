from decimal import Decimal
from typing import Protocol

from arbeitszeit_web.fields import FormField


class RequestEmailAddressChangeForm(Protocol):
    @property
    def new_email_field(self) -> FormField[str]:
        ...


class LoginMemberForm(Protocol):
    def email_field(self) -> FormField[str]:
        ...

    def password_field(self) -> FormField[str]:
        ...

    def remember_field(self) -> FormField[bool]:
        ...


class LoginCompanyForm(Protocol):
    def email_field(self) -> FormField[str]:
        ...

    def password_field(self) -> FormField[str]:
        ...

    def remember_field(self) -> FormField[bool]:
        ...


class LogInAccountantForm(Protocol):
    def email_field(self) -> FormField[str]:
        ...

    def password_field(self) -> FormField[str]:
        ...

    def remember_field(self) -> FormField[bool]:
        ...


class DraftForm(Protocol):
    def product_name_field(self) -> FormField[str]:
        ...

    def description_field(self) -> FormField[str]:
        ...

    def timeframe_field(self) -> FormField[int]:
        ...

    def unit_of_distribution_field(self) -> FormField[str]:
        ...

    def amount_field(self) -> FormField[int]:
        ...

    def means_cost_field(self) -> FormField[Decimal]:
        ...

    def resource_cost_field(self) -> FormField[Decimal]:
        ...

    def labour_cost_field(self) -> FormField[Decimal]:
        ...

    def is_public_service_field(self) -> FormField[bool]:
        ...


class RegisterPrivateConsumptionForm(Protocol):
    def amount_field(self) -> FormField[str]:
        ...

    def plan_id_field(self) -> FormField[str]:
        ...


class RegisterProductiveConsumptionForm(Protocol):
    def amount_field(self) -> FormField[str]:
        ...

    def plan_id_field(self) -> FormField[str]:
        ...

    def type_of_consumption_field(self) -> FormField[str]:
        ...


class RegisterForm(Protocol):
    @property
    def email_field(self) -> FormField[str]:
        ...

    @property
    def password_field(self) -> FormField[str]:
        ...

    @property
    def name_field(self) -> FormField[str]:
        ...


class RequestCoordinationTransferForm(Protocol):
    def candidate_field(self) -> FormField[str]:
        ...

    def cooperation_field(self) -> FormField[str]:
        ...
