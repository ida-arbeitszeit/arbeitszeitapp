from dataclasses import dataclass
from typing import Optional

from arbeitszeit.repositories import CompanyRepository, MemberRepository
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class MemberAuthenticator:
    member_repository: MemberRepository
    session: Session
    translator: Translator
    notifier: Notifier
    request: Request
    url_index: UrlIndex

    def redirect_user_to_member_login(self) -> Optional[str]:
        user_id = self.session.get_current_user()
        if not user_id:
            # not an authenticated user
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        elif not self.member_repository.get_members().with_id(user_id):
            # not a member
            self.notifier.display_warning(
                self.translator.gettext("You are not logged with the correct account.")
            )
            self.session.logout()
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        elif (
            not self.member_repository.get_members()
            .with_id(user_id)
            .that_are_confirmed()
        ):
            # not a confirmed member
            return self.url_index.get_unconfirmed_member_url()
        return None


@dataclass
class CompanyAuthenticator:
    company_repository: CompanyRepository
    session: Session
    translator: Translator
    notifier: Notifier
    request: Request
    url_index: UrlIndex

    def redirect_user_to_company_login(self) -> Optional[str]:
        user_id = self.session.get_current_user()
        if not user_id:
            # not an authenticated user
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        elif not self.company_repository.get_companies().with_id(user_id):
            # not a company
            self.notifier.display_warning(
                self.translator.gettext("You are not logged with the correct account.")
            )
            self.session.logout()
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        elif not self.company_repository.is_company_confirmed(user_id):
            # not a confirmed company
            return self.url_index.get_unconfirmed_company_url()
        return None
