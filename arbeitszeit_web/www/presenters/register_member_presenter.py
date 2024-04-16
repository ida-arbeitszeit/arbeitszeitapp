from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit_web.forms import RegisterForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class RegisterMemberViewModel:
    redirect_to: Optional[str]


@dataclass
class RegisterMemberPresenter:
    session: Session
    translator: Translator
    url_index: UrlIndex

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
            if (
                response.rejection_reason
                == RegisterMemberUseCase.Response.RejectionReason.company_with_different_password_exists
            ):
                form.email_field.attach_error(
                    self.translator.gettext(
                        "A company with the same email address already exists but the provided password does not match."
                    )
                )
            return RegisterMemberViewModel(redirect_to=None)
        else:
            assert response.user_id
            self.session.login_member(response.user_id)
            return RegisterMemberViewModel(
                redirect_to=(
                    self.url_index.get_unconfirmed_member_url()
                    if response.is_confirmation_required
                    else self.url_index.get_member_dashboard_url()
                ),
            )
