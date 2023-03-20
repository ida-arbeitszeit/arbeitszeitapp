from typing import Any, Callable, TypeVar, cast

import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from arbeitszeit.accountant_notifications import NotifyAccountantsAboutNewPlanPresenter
from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.token import InvitationTokenValidator, TokenService
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.dependency_injection import TestingModule
from tests.token import FakeTokenService

from . import repositories
from .notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)


def provide_social_accounting_instance(
    entity_storage: repositories.EntityStorage,
) -> entities.SocialAccounting:
    return entity_storage.social_accounting


class InMemoryModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[NotifyAccountantsAboutNewPlanPresenter] = AliasProvider(NotifyAccountantsAboutNewPlanPresenterImpl)  # type: ignore
        binder[interfaces.LanguageRepository] = AliasProvider(  # type: ignore
            repositories.FakeLanguageRepository
        )
        binder[interfaces.AccountantRepository] = AliasProvider(  # type: ignore
            repositories.AccountantRepositoryTestImpl
        )
        binder[AccountantInvitationPresenter] = AliasProvider(  # type: ignore
            AccountantInvitationPresenterTestImpl
        )
        binder[InvitationTokenValidator] = AliasProvider(FakeTokenService)  # type: ignore
        binder[InvitationTokenValidator] = AliasProvider(FakeTokenService)  # type: ignore
        binder[interfaces.TransactionRepository] = AliasProvider(  # type: ignore
            repositories.TransactionRepository
        )
        binder[interfaces.WorkerInviteRepository] = AliasProvider(  # type: ignore
            repositories.WorkerInviteRepository
        )
        binder[entities.SocialAccounting] = CallableProvider(
            provide_social_accounting_instance
        )
        binder[interfaces.AccountRepository] = AliasProvider(  # type: ignore
            repositories.AccountRepository
        )
        binder[interfaces.MemberRepository] = AliasProvider(  # type: ignore
            repositories.MemberRepository
        )
        binder[interfaces.MemberRepository] = AliasProvider(  # type: ignore
            repositories.MemberRepository
        )
        binder[interfaces.CompanyRepository] = AliasProvider(  # type: ignore
            repositories.CompanyRepository
        )
        binder[interfaces.PlanRepository] = AliasProvider(repositories.PlanRepository)  # type: ignore
        binder[interfaces.PlanDraftRepository] = AliasProvider(  # type: ignore
            repositories.PlanDraftRepository
        )
        binder[interfaces.AccountOwnerRepository] = AliasProvider(  # type: ignore
            repositories.AccountOwnerRepository
        )
        binder[interfaces.CooperationRepository] = AliasProvider(  # type: ignore
            repositories.CooperationRepository
        )
        binder[TokenService] = AliasProvider(FakeTokenService)  # type: ignore
        binder.bind(
            interfaces.DatabaseGateway,  # type: ignore
            to=AliasProvider(repositories.EntityStorage),
        )


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


CallableT = TypeVar("CallableT", bound=Callable)


def injection_test(original_test: CallableT) -> CallableT:
    injector = get_dependency_injector()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return injector.call_with_injection(original_test, args=args, kwargs=kwargs)

    return cast(CallableT, wrapper)
