from typing import Protocol

from arbeitszeit.use_cases.register_member import RegisterMemberUseCase


class RegisterForm(Protocol):
    def get_email_string(self) -> str:
        ...

    def get_name_string(self) -> str:
        ...

    def get_password_string(self) -> str:
        ...

    def add_email_error(self, error: str) -> None:
        ...


class RegisterMemberController:
    def create_request(
        self,
        register_form: RegisterForm,
    ) -> RegisterMemberUseCase.Request:
        return RegisterMemberUseCase.Request(
            email=register_form.get_email_string(),
            name=register_form.get_name_string(),
            password=register_form.get_password_string(),
        )
