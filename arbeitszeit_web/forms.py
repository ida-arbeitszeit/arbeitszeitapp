from typing import Protocol


class LoginMemberForm(Protocol):
    def add_email_error(self, error: str) -> None:
        ...

    def add_password_error(self, error: str) -> None:
        ...

    def get_remember_field(self) -> bool:
        ...


class LoginCompanyForm(Protocol):
    def add_password_error(self, error: str) -> None:
        ...

    def add_email_error(self, error: str) -> None:
        ...

    def get_remember_field(self) -> bool:
        ...
