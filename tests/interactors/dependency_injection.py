from typing import Any, Callable, TypeVar, cast

import arbeitszeit.email_notifications
import arbeitszeit.repositories as interfaces
import tests.email_notifications
from arbeitszeit import records
from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit_web.token import TokenService
from tests.dependency_injection import TestingModule
from tests.password_hasher import PasswordHasherImpl
from tests.token import FakeTokenService

from . import repositories


def provide_social_accounting_instance(
    mock_database: repositories.MockDatabase,
) -> records.SocialAccounting:
    return mock_database.social_accounting


def provide_email_sender() -> tests.email_notifications.EmailSenderTestImpl:
    return tests.email_notifications.EmailSenderTestImpl()


class InMemoryModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[interfaces.LanguageRepository] = AliasProvider(
            repositories.FakeLanguageRepository
        )
        binder[records.SocialAccounting] = CallableProvider(
            provide_social_accounting_instance
        )
        binder.bind(
            interfaces.DatabaseGateway,
            to=AliasProvider(repositories.MockDatabase),
        )
        binder.bind(
            PasswordHasher,
            to=AliasProvider(PasswordHasherImpl),
        )
        binder.bind(
            TokenService,
            to=AliasProvider(FakeTokenService),
        )
        binder[arbeitszeit.email_notifications.EmailSender] = AliasProvider(
            tests.email_notifications.EmailSenderTestImpl
        )
        binder[tests.email_notifications.EmailSenderTestImpl] = CallableProvider(
            provide_email_sender, is_singleton=True
        )


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


CallableT = TypeVar("CallableT", bound=Callable)


def injection_test(original_test: CallableT) -> CallableT:
    injector = get_dependency_injector()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return injector.call_with_injection(original_test, args=args, kwargs=kwargs)

    return cast(CallableT, wrapper)
