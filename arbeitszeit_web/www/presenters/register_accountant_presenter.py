from dataclasses import dataclass
from typing import Optional

from arbeitszeit.interactors.register_accountant import RegisterAccountantInteractor
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


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
        self, response: RegisterAccountantInteractor.Response
    ) -> ViewModel:
        if response.is_accepted:
            assert response.user_id
            self.session.login_accountant(accountant=response.user_id)
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
