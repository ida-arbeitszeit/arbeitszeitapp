from injector import Injector, Module, inject, provider, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from arbeitszeit.accountant_notifications import NotifyAccountantsAboutNewPlanPresenter
from arbeitszeit.token import InvitationTokenValidator, TokenService
from arbeitszeit.use_cases import GetCompanySummary
from arbeitszeit.use_cases.edit_draft import EditDraftUseCase
from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.dependency_injection import TestingModule
from tests.token import FakeTokenService, TokenDeliveryService

from . import repositories
from .notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)


class InMemoryModule(Module):
    @singleton
    @provider
    def provide_fake_language_repository(self) -> repositories.FakeLanguageRepository:
        return repositories.FakeLanguageRepository()

    @provider
    def provide_notify_accountants_about_new_plan_presenter(
        self, instance: NotifyAccountantsAboutNewPlanPresenterImpl
    ) -> NotifyAccountantsAboutNewPlanPresenter:
        return instance

    @provider
    def provide_language_repository(
        self, language_repository: repositories.FakeLanguageRepository
    ) -> interfaces.LanguageRepository:
        return language_repository

    @provider
    def provide_accountant_repository(
        self, repository: repositories.AccountantRepositoryTestImpl
    ) -> interfaces.AccountantRepository:
        return repository

    @singleton
    @provider
    def provide_accountant_invitation_presenter_test_impl(
        self,
    ) -> AccountantInvitationPresenterTestImpl:
        return AccountantInvitationPresenterTestImpl()

    @provider
    def provide_accountant_invitation_presenter(
        self, presenter: AccountantInvitationPresenterTestImpl
    ) -> AccountantInvitationPresenter:
        return presenter

    @provider
    def provide_invitation_token_validator(
        self, token_service: FakeTokenService
    ) -> InvitationTokenValidator:
        return token_service

    @provider
    @singleton
    def provide_token_delivery_service(self) -> TokenDeliveryService:
        return TokenDeliveryService()

    @provider
    def provide_purchase_repo(
        self, repo: repositories.PurchaseRepository
    ) -> interfaces.PurchaseRepository:
        return repo

    @provider
    def provide_transaction_repo(
        self, repo: repositories.TransactionRepository
    ) -> interfaces.TransactionRepository:
        return repo

    @provider
    @singleton
    def provide_worker_invite_repo(
        self, repo: repositories.WorkerInviteRepository
    ) -> interfaces.WorkerInviteRepository:
        return repo

    @provider
    @singleton
    def provide_social_accounting_instance(
        self, entity_storage: repositories.EntityStorage
    ) -> entities.SocialAccounting:
        return entity_storage.social_accounting

    @provider
    def provide_account_repository(
        self, repo: repositories.AccountRepository
    ) -> interfaces.AccountRepository:
        return repo

    @provider
    def provide_member_repository(
        self, repo: repositories.MemberRepository
    ) -> interfaces.MemberRepository:
        return repo

    @provider
    def provide_company_repository(
        self, repo: repositories.CompanyRepository
    ) -> interfaces.CompanyRepository:
        return repo

    @provider
    def provide_plan_repository(
        self, repo: repositories.PlanRepository
    ) -> interfaces.PlanRepository:
        return repo

    @provider
    def proved_plan_draft_repository(
        self,
        repo: repositories.PlanDraftRepository,
    ) -> interfaces.PlanDraftRepository:
        return repo

    @provider
    def provide_account_owner_repository(
        self, repo: repositories.AccountOwnerRepository
    ) -> interfaces.AccountOwnerRepository:
        return repo

    @provider
    def provide_cooperation_repository(
        self, repo: repositories.CooperationRepository
    ) -> interfaces.CooperationRepository:
        return repo

    @provider
    def provide_plan_cooperation_repository(
        self, repo: repositories.PlanCooperationRepository
    ) -> interfaces.PlanCooperationRepository:
        return repo

    @singleton
    @provider
    def provide_payout_factor_repository(
        self, repo: repositories.FakePayoutFactorRepository
    ) -> interfaces.PayoutFactorRepository:
        return repo

    @provider
    def provide_token_service(self, token_service: FakeTokenService) -> TokenService:
        return token_service

    @provider
    def provide_get_company_summary(
        self,
        company_repository: interfaces.CompanyRepository,
        plan_repository: interfaces.PlanRepository,
        account_repository: interfaces.AccountRepository,
        transaction_repository: interfaces.TransactionRepository,
        social_accounting: entities.SocialAccounting,
        purchase_repository: interfaces.PurchaseRepository,
    ) -> GetCompanySummary:
        return GetCompanySummary(
            company_repository,
            plan_repository,
            account_repository,
            transaction_repository,
            social_accounting,
            purchase_repository,
        )

    @provider
    def provide_log_in_member_use_case(
        self, member_repository: interfaces.MemberRepository
    ) -> LogInMemberUseCase:
        return LogInMemberUseCase(member_repository=member_repository)

    @singleton
    @provider
    def provide_control_thresholds_test_impl(self) -> ControlThresholdsTestImpl:
        return ControlThresholdsTestImpl()

    @provider
    def provide_list_available_languages_use_case(
        self, language_repository: interfaces.LanguageRepository
    ) -> ListAvailableLanguagesUseCase:
        return ListAvailableLanguagesUseCase(language_repository=language_repository)

    @provider
    def provide_log_in_company_use_case(
        self, company_repository: interfaces.CompanyRepository
    ) -> LogInCompanyUseCase:
        return LogInCompanyUseCase(company_repository=company_repository)

    @provider
    def provide_edit_draft_use_case(
        self, draft_repository: interfaces.PlanDraftRepository
    ) -> EditDraftUseCase:
        return EditDraftUseCase(draft_repository=draft_repository)


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
