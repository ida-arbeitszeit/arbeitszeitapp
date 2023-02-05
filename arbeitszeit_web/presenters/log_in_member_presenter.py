from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.forms import LoginMemberForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class LogInMemberPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    translator: Translator
    member_url_index: UrlIndex

    def present_login_process(
        self, response: LogInMemberUseCase.Response, form: LoginMemberForm
    ) -> ViewModel:
        if response.is_logged_in:
            assert response.user_id
            self.session.login_member(
                member=response.user_id, remember=form.remember_field().get_value()
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
                form.email_field().attach_error(
                    self.translator.gettext(
                        "Email address incorrect. Are you already registered as a member?"
                    ),
                )
            else:
                form.password_field().attach_error(
                    self.translator.gettext("Incorrect password"),
                )
            return self.ViewModel(redirect_url=None)
