from arbeitszeit.injector import AliasProvider, Binder, Injector, Module
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.email.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.url_index import UrlIndex
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import TestingModule
from tests.email import FakeEmailConfiguration, FakeEmailService
from tests.email_presenters.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from tests.language_service import FakeLanguageService
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.use_cases.dependency_injection import InMemoryModule

from .presenters.notifier import NotifierTestImpl
from .presenters.url_index import UrlIndexTestImpl


class WwwTestsInjector(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[AccountantInvitationEmailView] = AliasProvider(
            AccountantInvitationEmailViewImpl
        )
        binder[EmailConfiguration] = AliasProvider(FakeEmailConfiguration)
        binder[Notifier] = AliasProvider(NotifierTestImpl)
        binder[UrlIndex] = AliasProvider(UrlIndexTestImpl)
        binder[Session] = AliasProvider(FakeSession)
        binder[Request] = AliasProvider(FakeRequest)
        binder[LanguageService] = AliasProvider(FakeLanguageService)
        binder[MailService] = AliasProvider(FakeEmailService)
        binder[DatetimeFormatter] = AliasProvider(FakeDatetimeService)


def get_dependency_injector() -> Injector:
    return Injector(modules=[TestingModule(), InMemoryModule(), WwwTestsInjector()])
