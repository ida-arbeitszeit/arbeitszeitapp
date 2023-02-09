import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from arbeitszeit.accountant_notifications import NotifyAccountantsAboutNewPlanPresenter
from arbeitszeit.injector import (
    Binder,
    CallableProvider,
    ClassProvider,
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
        binder[NotifyAccountantsAboutNewPlanPresenter] = ClassProvider(NotifyAccountantsAboutNewPlanPresenterImpl)  # type: ignore
        binder[interfaces.LanguageRepository] = ClassProvider(  # type: ignore
            repositories.FakeLanguageRepository
        )
        binder[interfaces.AccountantRepository] = ClassProvider(  # type: ignore
            repositories.AccountantRepositoryTestImpl
        )
        binder[AccountantInvitationPresenter] = ClassProvider(  # type: ignore
            AccountantInvitationPresenterTestImpl
        )
        binder[InvitationTokenValidator] = ClassProvider(FakeTokenService)  # type: ignore
        binder[InvitationTokenValidator] = ClassProvider(FakeTokenService)  # type: ignore
        binder[interfaces.PurchaseRepository] = ClassProvider(  # type: ignore
            repositories.PurchaseRepository
        )
        binder[interfaces.TransactionRepository] = ClassProvider(  # type: ignore
            repositories.TransactionRepository
        )
        binder[interfaces.WorkerInviteRepository] = ClassProvider(  # type: ignore
            repositories.WorkerInviteRepository
        )
        binder[entities.SocialAccounting] = CallableProvider(
            provide_social_accounting_instance
        )
        binder[interfaces.AccountRepository] = ClassProvider(  # type: ignore
            repositories.AccountRepository
        )
        binder[repositories.AccountRepository] = ClassProvider(
            repositories.AccountRepository
        )
        binder[interfaces.MemberRepository] = ClassProvider(  # type: ignore
            repositories.MemberRepository
        )
        binder[interfaces.MemberRepository] = ClassProvider(  # type: ignore
            repositories.MemberRepository
        )
        binder[interfaces.CompanyRepository] = ClassProvider(  # type: ignore
            repositories.CompanyRepository
        )
        binder[interfaces.PlanRepository] = ClassProvider(repositories.PlanRepository)  # type: ignore
        binder[interfaces.PlanDraftRepository] = ClassProvider(  # type: ignore
            repositories.PlanDraftRepository
        )
        binder[interfaces.AccountOwnerRepository] = ClassProvider(  # type: ignore
            repositories.AccountOwnerRepository
        )
        binder[interfaces.CooperationRepository] = ClassProvider(  # type: ignore
            repositories.CooperationRepository
        )
        binder[interfaces.PayoutFactorRepository] = ClassProvider(  # type: ignore
            repositories.FakePayoutFactorRepository
        )
        binder[TokenService] = ClassProvider(FakeTokenService)  # type: ignore


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(original_test, args=args, kwargs=kwargs)

    return wrapper
