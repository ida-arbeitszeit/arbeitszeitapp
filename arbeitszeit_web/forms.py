from decimal import Decimal
from typing import Protocol

from arbeitszeit_web.fields import FormField


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
