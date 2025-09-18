from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.interactors.log_in_company import LogInCompanyInteractor
from arbeitszeit_web.forms import LoginCompanyForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class LogInCompanyPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    url_index: UrlIndex
    translator: Translator

    def present_login_process(
        self, response: LogInCompanyInteractor.Response, form: LoginCompanyForm
    ) -> ViewModel:
        if response.is_logged_in and response.email_address:
            assert response.user_id
            self.session.login_company(
                company=response.user_id, remember=form.remember_field().get_value()
            )
            redirect_url = (
                self.session.pop_next_url()
                or self.url_index.get_company_dashboard_url()
            )
        else:
            if (
                response.rejection_reason
                == LogInCompanyInteractor.RejectionReason.invalid_password
            ):
                form.password_field().attach_error(
                    self.translator.gettext("Password is incorrect")
                )
            else:
                form.email_field().attach_error(
                    self.translator.gettext(
                        "Email address is not correct. Are you already signed up?"
                    )
                )
            redirect_url = None
        return self.ViewModel(redirect_url=redirect_url)
