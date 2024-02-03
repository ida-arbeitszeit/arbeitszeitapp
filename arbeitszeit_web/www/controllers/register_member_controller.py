from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit_web.forms import RegisterForm


class RegisterMemberController:
    def create_request(
        self,
        form: RegisterForm,
    ) -> RegisterMemberUseCase.Request:
        return RegisterMemberUseCase.Request(
            email=form.email_field.get_value(),
            name=form.name_field.get_value(),
            password=form.password_field.get_value(),
        )
