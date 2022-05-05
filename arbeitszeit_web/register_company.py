from typing import Protocol

from arbeitszeit.use_cases import RegisterCompany


class RegisterForm(Protocol):
    def get_email_string(self) -> str:
        ...

    def get_name_string(self) -> str:
        ...

    def get_password_string(self) -> str:
        ...

    def add_email_error(self, message: str) -> None:
        ...


class RegisterCompanyController:
    def create_request(
        self,
        register_form: RegisterForm,
    ) -> RegisterCompany.Request:
        return RegisterCompany.Request(
            email=register_form.get_email_string(),
            name=register_form.get_name_string(),
            password=register_form.get_password_string(),
        )
