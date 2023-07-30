from arbeitszeit.injector import AliasProvider, Binder, Injector, Module
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.url_index import (
    AccountantInvitationUrlIndex,
    HidePlanUrlIndex,
    LanguageChangerUrlIndex,
    RenewPlanUrlIndex,
    UrlIndex,
)
from arbeitszeit_web.www.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from tests.dependency_injection import TestingModule
from tests.email import FakeEmailConfiguration, FakeEmailSender
from tests.language_service import FakeLanguageService
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.use_cases.dependency_injection import InMemoryModule

from .accountant_invitation_email_view import AccountantInvitationEmailViewImpl
from .notifier import NotifierTestImpl
from .url_index import (
    AccountantInvitationUrlIndexImpl,
    HidePlanUrlIndexTestImpl,
    LanguageChangerUrlIndexImpl,
    RenewPlanUrlIndexTestImpl,
    UrlIndexTestImpl,
)


class PresenterTestsInjector(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[AccountantInvitationEmailView] = AliasProvider(  # type: ignore
            AccountantInvitationEmailViewImpl
        )
        binder[EmailConfiguration] = AliasProvider(FakeEmailConfiguration)  # type: ignore
        binder[AccountantInvitationUrlIndex] = AliasProvider(AccountantInvitationUrlIndexImpl)  # type: ignore
        binder[Notifier] = AliasProvider(NotifierTestImpl)  # type: ignore
        binder[UrlIndex] = AliasProvider(UrlIndexTestImpl)
        binder[Session] = AliasProvider(FakeSession)  # type: ignore
        binder[Request] = AliasProvider(FakeRequest)  # type: ignore
        binder[LanguageChangerUrlIndex] = AliasProvider(LanguageChangerUrlIndexImpl)  # type: ignore
        binder[LanguageService] = AliasProvider(FakeLanguageService)  # type: ignore
        binder[MailService] = AliasProvider(FakeEmailSender)  # type: ignore
        binder[RenewPlanUrlIndex] = AliasProvider(RenewPlanUrlIndexTestImpl)  # type: ignore
        binder[HidePlanUrlIndex] = AliasProvider(HidePlanUrlIndexTestImpl)  # type: ignore


def get_dependency_injector() -> Injector:
    return Injector(
        modules=[TestingModule(), InMemoryModule(), PresenterTestsInjector()]
    )
