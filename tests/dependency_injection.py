from injector import Injector, Module, inject, provider

import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from tests import data_generators, repositories


class RepositoryModule(Module):
    @provider
    def provide_offer_repository(
        self, repo: repositories.OfferRepository
    ) -> interfaces.OfferRepository:
        return repo

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
    def provide_company_worker_repo(
        self, repo: repositories.CompanyWorkerRepository
    ) -> interfaces.CompanyWorkerRepository:
        return repo

    @provider
    def provide_social_accounting_instance(self) -> entities.SocialAccounting:
        return data_generators.SocialAccountingGenerator(
            data_generators.AccountGenerator(data_generators.IdGenerator())
        ).create_social_accounting()

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


def injection_test(original_test):
    injector = Injector(RepositoryModule())

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
