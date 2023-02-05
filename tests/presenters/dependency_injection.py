from arbeitszeit.injector import Binder, ClassProvider, Injector, Module
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.url_index import (
    AccountantInvitationUrlIndex,
    HidePlanUrlIndex,
    LanguageChangerUrlIndex,
    RenewPlanUrlIndex,
    UrlIndex,
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
        binder[AccountantInvitationEmailView] = ClassProvider(  # type: ignore
            AccountantInvitationEmailViewImpl
        )
        binder[EmailConfiguration] = ClassProvider(FakeEmailConfiguration)  # type: ignore
        binder[AccountantInvitationUrlIndex] = ClassProvider(AccountantInvitationUrlIndexImpl)  # type: ignore
        binder[Notifier] = ClassProvider(NotifierTestImpl)  # type: ignore
        binder[UrlIndex] = ClassProvider(UrlIndexTestImpl)
        binder[Session] = ClassProvider(FakeSession)  # type: ignore
        binder[Request] = ClassProvider(FakeRequest)  # type: ignore
        binder[LanguageChangerUrlIndex] = ClassProvider(LanguageChangerUrlIndexImpl)  # type: ignore
        binder[LanguageService] = ClassProvider(FakeLanguageService)  # type: ignore
        binder[MailService] = ClassProvider(FakeEmailSender)  # type: ignore
        binder[RenewPlanUrlIndex] = ClassProvider(RenewPlanUrlIndexTestImpl)  # type: ignore
        binder[HidePlanUrlIndex] = ClassProvider(HidePlanUrlIndexTestImpl)  # type: ignore


def get_dependency_injector() -> Injector:
    return Injector(
        modules=[TestingModule(), InMemoryModule(), PresenterTestsInjector()]
    )


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(original_test, args=args, kwargs=kwargs)

    return wrapper
