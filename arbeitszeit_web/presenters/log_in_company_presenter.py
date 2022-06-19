from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit_web.forms import LoginCompanyForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import CompanyUrlIndex


@dataclass
class LogInCompanyPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    company_url_index: CompanyUrlIndex
    translator: Translator

    def present_login_process(
        self, response: LogInCompanyUseCase.Response, form: LoginCompanyForm
    ) -> ViewModel:
        if response.is_logged_in and response.email_address:
            self.session.login_company(
                response.email_address, form.get_remember_field()
            )
            redirect_url = (
                self.session.pop_next_url()
                or self.company_url_index.get_company_dashboard_url()
            )
        else:
            if (
                response.rejection_reason
                == LogInCompanyUseCase.RejectionReason.invalid_password
            ):
                form.add_password_error(
                    self.translator.gettext("Password is incorrect")
                )
            else:
                form.add_email_error(
                    self.translator.gettext(
                        "Email address is not correct. Are you already signed up?"
                    )
                )
            redirect_url = None
        return self.ViewModel(redirect_url=redirect_url)
