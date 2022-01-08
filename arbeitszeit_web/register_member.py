from arbeitszeit.use_cases import RegisterMemberRequest
from typing import Protocol


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
        email_subject: str,
        email_html: str,
        email_sender: str,
    ) -> RegisterMemberRequest:
        return RegisterMemberRequest(
            email=register_form.get_email_string(),
            name=register_form.get_name_string(),
            password=register_form.get_password_string(),
            email_subject=email_subject,
            email_html=email_html,
            email_sender=email_sender,
        )
