from dataclasses import dataclass

from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit_web.forms import RegisterForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class RegisterMemberViewModel:
    is_success_view: bool


@dataclass
class RegisterMemberPresenter:
    session: Session
    translator: Translator

    def present_member_registration(
        self, response: RegisterMemberUseCase.Response, form: RegisterForm
    ) -> RegisterMemberViewModel:
        if response.is_rejected:
            if (
                response.rejection_reason
                == RegisterMemberUseCase.Response.RejectionReason.member_already_exists
            ):
                form.email_field.attach_error(
                    self.translator.gettext("This email address is already registered.")
                )
            return RegisterMemberViewModel(is_success_view=False)
        else:
            assert response.user_id
            self.session.login_member(response.user_id)
            return RegisterMemberViewModel(is_success_view=True)
