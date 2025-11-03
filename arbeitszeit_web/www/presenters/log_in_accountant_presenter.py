from dataclasses import dataclass
from typing import Optional

from arbeitszeit.interactors.log_in_accountant import (
    LogInAccountantInteractor as Interactor,
)
from arbeitszeit_web.forms import LogInAccountantForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class LogInAccountantPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    url_index: UrlIndex
    translator: Translator

    def present_login_process(
        self, form: LogInAccountantForm, response: Interactor.Response
    ) -> ViewModel:
        if response.user_id is None:
            if response.rejection_reason == Interactor.RejectionReason.wrong_password:
                form.password_field().attach_error(
                    self.translator.gettext("Incorrect password")
                )
            elif (
                response.rejection_reason
                == Interactor.RejectionReason.email_is_not_accountant
            ):
                form.email_field().attach_error(
                    self.translator.gettext(
                        "This email address does not belong to a registered accountant"
                    )
                )
            return self.ViewModel(redirect_url=None)
        self.session.login_accountant(
            accountant=response.user_id,
            remember=form.remember_field().get_value(),
        )
        return self.ViewModel(
            redirect_url=self.session.pop_next_url()
            or self.url_index.get_accountant_dashboard_url()
        )
