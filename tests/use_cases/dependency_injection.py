from injector import Injector, Module, inject, provider, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.token import InvitationTokenValidator, TokenDeliverer, TokenService
from arbeitszeit.use_cases import GetCompanySummary
from arbeitszeit.use_cases.get_accountant_profile_info import (
    GetAccountantProfileInfoUseCase,
)
from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit.use_cases.register_company.company_registration_message_presenter import (
    CompanyRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.register_member.member_registration_message_presenter import (
    MemberRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from tests import data_generators
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import TestingModule
from tests.token import FakeTokenService, TokenDeliveryService

from . import repositories


class InMemoryModule(Module):
    @singleton
    @provider
    def provide_accoutant_repository_test_impl(
        self,
    ) -> repositories.AccountantRepositoryTestImpl:
        return repositories.AccountantRepositoryTestImpl()

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
    def provide_company_registration_message_presenter(
        self, token_delivery_service: TokenDeliveryService
    ) -> CompanyRegistrationMessagePresenter:
        return token_delivery_service

    @provider
    def provide_member_registration_message_presenter(
        self, token_delivery_service: TokenDeliveryService
    ) -> MemberRegistrationMessagePresenter:
        return token_delivery_service

    @provider
    @singleton
    def provide_token_delivery_service(self) -> TokenDeliveryService:
        return TokenDeliveryService()

    @provider
    def provide_token_deliverer(self, service: TokenDeliveryService) -> TokenDeliverer:
        return service

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
    def provide_message_repo(
        self, repo: repositories.MessageRepository
    ) -> interfaces.MessageRepository:
        return repo

    @provider
    def provide_company_worker_repo(
        self, repo: repositories.CompanyWorkerRepository
    ) -> interfaces.CompanyWorkerRepository:
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
        self, generator: data_generators.SocialAccountingGenerator
    ) -> entities.SocialAccounting:
        return generator.create_social_accounting()

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

    @provider
    @singleton
    def provide_datetime_service(self, service: FakeDatetimeService) -> DatetimeService:
        return service

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
    ) -> GetCompanySummary:
        return GetCompanySummary(
            company_repository,
            plan_repository,
            account_repository,
            transaction_repository,
            social_accounting,
        )

    @provider
    def provide_get_accountant_profile_info_use_case(
        self, accountant_repository: interfaces.AccountantRepository
    ) -> GetAccountantProfileInfoUseCase:
        return GetAccountantProfileInfoUseCase(
            accountant_repository=accountant_repository,
        )

    @provider
    def provide_log_in_accountant_use_case(
        self, accountant_repository: interfaces.AccountantRepository
    ) -> LogInAccountantUseCase:
        return LogInAccountantUseCase(
            accountant_repository=accountant_repository,
        )

    @provider
    def provide_log_in_member_use_case(
        self, member_repository: interfaces.MemberRepository
    ) -> LogInMemberUseCase:
        return LogInMemberUseCase(member_repository=member_repository)


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
