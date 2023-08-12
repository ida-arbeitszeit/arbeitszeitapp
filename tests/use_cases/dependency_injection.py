from typing import Any, Callable, TypeVar, cast

import arbeitszeit.repositories as interfaces
from arbeitszeit import records
from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.presenters import (
    AccountantInvitationPresenter,
    InviteWorkerPresenter,
    NotifyAccountantsAboutNewPlanPresenter,
)
from arbeitszeit_web.token import TokenService
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.dependency_injection import TestingModule
from tests.password_hasher import PasswordHasherImpl
from tests.token import FakeTokenService
from tests.work_invitation_presenter import InviteWorkerPresenterImpl

from . import repositories
from .notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)


def provide_social_accounting_instance(
    mock_database: repositories.MockDatabase,
) -> records.SocialAccounting:
    return mock_database.social_accounting


class InMemoryModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[NotifyAccountantsAboutNewPlanPresenter] = AliasProvider(NotifyAccountantsAboutNewPlanPresenterImpl)  # type: ignore
        binder[interfaces.LanguageRepository] = AliasProvider(  # type: ignore
            repositories.FakeLanguageRepository
        )
        binder[AccountantInvitationPresenter] = AliasProvider(  # type: ignore
            AccountantInvitationPresenterTestImpl
        )
        binder[InviteWorkerPresenter] = AliasProvider(InviteWorkerPresenterImpl)  # type: ignore
        binder[records.SocialAccounting] = CallableProvider(
            provide_social_accounting_instance
        )
        binder.bind(
            interfaces.DatabaseGateway,  # type: ignore
            to=AliasProvider(repositories.MockDatabase),
        )
        binder.bind(
            PasswordHasher,  # type: ignore
            to=AliasProvider(PasswordHasherImpl),
        )
        binder.bind(
            TokenService,  # type: ignore
            to=AliasProvider(FakeTokenService),
        )


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


CallableT = TypeVar("CallableT", bound=Callable)


def injection_test(original_test: CallableT) -> CallableT:
    injector = get_dependency_injector()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return injector.call_with_injection(original_test, args=args, kwargs=kwargs)

    return cast(CallableT, wrapper)
