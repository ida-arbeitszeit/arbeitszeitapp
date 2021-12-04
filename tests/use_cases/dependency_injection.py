from injector import Injector, Module, inject, provider, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from arbeitszeit.datetime_service import DatetimeService
from tests import data_generators
from tests.datetime_service import FakeDatetimeService

from . import repositories


class InMemoryModule(Module):
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


def get_dependency_injector() -> Injector:
    return Injector(InMemoryModule())


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
