from dataclasses import dataclass
from typing import Optional

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class MemberAuthenticator:
    database: DatabaseGateway
    session: Session
    translator: Translator
    notifier: Notifier
    request: Request
    url_index: UrlIndex

    def is_unconfirmed_member(self) -> bool:
        user_id = self.session.get_current_user()
        if not user_id:
            return False
        record = (
            self.database.get_members()
            .with_id(user_id)
            .joined_with_email_address()
            .first()
        )
        if not record:
            return False
        _, email = record
        return email.confirmed_on is None

    def redirect_user_to_member_login(self) -> Optional[str]:
        user_id = self.session.get_current_user()
        if not user_id:
            # not an authenticated user
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        elif not self.database.get_members().with_id(user_id):
            # not a member
            self.notifier.display_warning(
                self.translator.gettext(
                    "You are not logged in with the correct account."
                )
            )
            self.session.logout()
            return self.url_index.get_start_page_url()
        elif not self.database.get_members().with_id(user_id).that_are_confirmed():
            # not a confirmed member
            return self.url_index.get_unconfirmed_member_url()
        return None


@dataclass
class CompanyAuthenticator:
    database: DatabaseGateway
    session: Session
    translator: Translator
    notifier: Notifier
    request: Request
    url_index: UrlIndex

    def is_unconfirmed_company(self) -> bool:
        user_id = self.session.get_current_user()
        if not user_id:
            return False
        record = (
            self.database.get_companies()
            .with_id(user_id)
            .joined_with_email_address()
            .first()
        )
        if not record:
            return False
        _, email = record
        return email.confirmed_on is None

    def redirect_user_to_company_login(self) -> Optional[str]:
        user_id = self.session.get_current_user()
        if not user_id:
            # not an authenticated user
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        elif not self.database.get_companies().with_id(user_id):
            # not a company
            self.notifier.display_warning(
                self.translator.gettext(
                    "You are not logged in with the correct account."
                )
            )
            self.session.logout()
            return self.url_index.get_start_page_url()
        elif not self.database.get_companies().with_id(user_id).that_are_confirmed():
            # not a confirmed company
            return self.url_index.get_unconfirmed_company_url()
        return None
