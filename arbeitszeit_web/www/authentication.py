from dataclasses import dataclass
from typing import Optional

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session, UserRole
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
            self.database.get_email_addresses().that_belong_to_member(user_id).first()
        )
        if not record:
            return False
        email = record
        return email.confirmed_on is None

    def redirect_user_to_member_login(self) -> Optional[str]:
        user_id = self.session.get_current_user()
        if not user_id:
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()
        else:
            email = (
                self.database.get_email_addresses()
                .that_belong_to_member(user_id)
                .first()
            )
            if email:
                if not email.confirmed_on:
                    return self.url_index.get_unconfirmed_member_url()
                else:
                    return None
            else:
                self._notify_incorrect_account()
                self.session.logout()
                return self.url_index.get_start_page_url()

    def _notify_incorrect_account(self) -> None:
        self.notifier.display_warning(
            self.translator.gettext("You are not logged in with the correct account.")
        )


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
        email = (
            self.database.get_email_addresses().that_belong_to_company(user_id).first()
        )
        if not email:
            return False
        return email.confirmed_on is None

    def redirect_user_to_company_login(self) -> Optional[str]:
        user_id = self.session.get_current_user()
        if user_id:
            email = (
                self.database.get_email_addresses()
                .that_belong_to_company(user_id)
                .first()
            )
            if email:
                if email.confirmed_on:
                    return None
                else:
                    return self.url_index.get_unconfirmed_company_url()
            else:
                self.notifier.display_warning(
                    self.translator.gettext(
                        "You are not logged in with the correct account."
                    )
                )
                self.session.logout()
                return self.url_index.get_start_page_url()
        else:
            # not an authenticated user
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            self.session.set_next_url(self.request.get_request_target())
            return self.url_index.get_start_page_url()


@dataclass
class AccountantAuthenticator:
    session: Session
    notifier: Notifier
    request: Request
    translator: Translator
    url_index: UrlIndex

    def redirect_unauthenticated_user_to_start_page(self) -> str | None:
        user_role = self.session.get_user_role()
        if not user_role:
            self.session.set_next_url(self.request.get_request_target())
            self.notifier.display_warning(
                self.translator.gettext("Please log in to view this page.")
            )
            return self.url_index.get_start_page_url()
        elif user_role == UserRole.accountant:
            return None
        else:
            self.notifier.display_warning(
                self.translator.gettext(
                    "You are not logged in with the correct account."
                )
            )
            self.session.logout()
            return self.url_index.get_start_page_url()


@dataclass
class UserAuthenticator:
    session: Session
    request: Request
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def is_user_authenticated(self) -> bool:
        return bool(self.session.get_current_user())

    def redirect_user_to_start_page(self) -> str:
        self.session.set_next_url(self.request.get_request_target())
        self.notifier.display_warning(
            self.translator.gettext("Please log in to view this page.")
        )
        return self.url_index.get_start_page_url()
