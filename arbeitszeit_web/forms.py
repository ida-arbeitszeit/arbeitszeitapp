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


class PayConsumerProductForm(Protocol):
    def amount_field(self) -> FormField[str]:
        ...

    def plan_id_field(self) -> FormField[str]:
        ...
