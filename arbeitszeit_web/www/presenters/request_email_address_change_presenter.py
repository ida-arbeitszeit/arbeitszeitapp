from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases import request_email_address_change as use_case
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session, UserRole
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: Optional[str]


@dataclass
class RequestEmailAddressChangePresenter:
    url_index: UrlIndex
    session: Session
    notifier: Notifier
    translator: Translator

    def render_response(self, uc_response: use_case.Response) -> ViewModel:
        redirect_url: Optional[str]
        if uc_response.is_rejected:
            redirect_url = None
            self.notifier.display_warning(
                self.translator.gettext(
                    "Your request for an email address change was rejected."
                )
            )
        elif self.session.get_user_role() == UserRole.member:
            redirect_url = self.url_index.get_member_account_details_url()
        elif self.session.get_user_role() == UserRole.accountant:
            redirect_url = self.url_index.get_accountant_account_details_url()
        else:
            redirect_url = self.url_index.get_company_account_details_url()
        return ViewModel(redirect_url=redirect_url)
