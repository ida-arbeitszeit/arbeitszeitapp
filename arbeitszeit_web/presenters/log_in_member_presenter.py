from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.forms import LoginMemberForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import MemberUrlIndex


@dataclass
class LogInMemberPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    translator: Translator
    member_url_index: MemberUrlIndex

    def present_login_process(
        self, response: LogInMemberUseCase.Response, form: LoginMemberForm
    ) -> ViewModel:
        if response.is_logged_in:
            self.session.login_member(
                email=response.email, remember=form.get_remember_field()
            )
            next_url = (
                self.session.pop_next_url()
                or self.member_url_index.get_member_dashboard_url()
            )
            return self.ViewModel(redirect_url=next_url)
        else:
            if (
                response.rejection_reason
                == LogInMemberUseCase.RejectionReason.unknown_email_address
            ):
                form.add_email_error(
                    self.translator.gettext(
                        "Email address incorrect. Are you already registered as a member?"
                    ),
                )
            else:
                form.add_password_error(
                    self.translator.gettext("Incorrect password"),
                )
            return self.ViewModel(redirect_url=None)
