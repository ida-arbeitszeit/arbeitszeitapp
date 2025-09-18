from arbeitszeit.interactors.register_member import RegisterMemberInteractor
from arbeitszeit_web.forms import RegisterForm


class RegisterMemberController:
    def create_request(
        self,
        form: RegisterForm,
    ) -> RegisterMemberInteractor.Request:
        return RegisterMemberInteractor.Request(
            email=form.email_field.get_value(),
            name=form.name_field.get_value(),
            password=form.password_field.get_value(),
        )
