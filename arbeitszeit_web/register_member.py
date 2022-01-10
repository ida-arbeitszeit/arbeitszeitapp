from typing import Protocol

from arbeitszeit.use_cases import RegisterMemberRequest


class RegisterForm(Protocol):
    def get_email_string(self) -> str:
        ...

    def get_name_string(self) -> str:
        ...

    def get_password_string(self) -> str:
        ...


class RegisterMemberController:
    def create_request(
        self,
        register_form: RegisterForm,
        email_sender: str,
        template_name: str,
        endpoint: str,
    ) -> RegisterMemberRequest:
        return RegisterMemberRequest(
            email=register_form.get_email_string(),
            name=register_form.get_name_string(),
            password=register_form.get_password_string(),
            email_sender=email_sender,
            template_name=template_name,
            endpoint=endpoint,
        )
