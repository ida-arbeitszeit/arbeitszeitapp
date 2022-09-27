from dataclasses import dataclass
from typing import Optional

from injector import inject

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@inject
@dataclass
class RegisterAccountantPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    notifier: Notifier
    session: Session
    translator: Translator
    dashboard_url_index: UrlIndex

    def present_registration_result(
        self, response: RegisterAccountantUseCase.Response
    ) -> ViewModel:
        if response.is_accepted:
            self.session.login_accountant(response.email_address)
            return self.ViewModel(
                redirect_url=self.dashboard_url_index.get_accountant_dashboard_url()
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext(
                    "Could not register %(email_address)s as an accountant"
                )
                % dict(email_address=response.email_address)
            )
            return self.ViewModel(redirect_url=None)
