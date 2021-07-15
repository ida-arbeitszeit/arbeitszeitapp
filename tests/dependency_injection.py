from injector import Injector, Module, inject, provider

import arbeitszeit.repositories as interfaces
from tests import repositories


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

    def provide_transaction_repo(
        self, repo: repositories.TransactionRepository
    ) -> interfaces.TransactionRepository:
        return repo


def injection_test(original_test):
    injector = Injector(RepositoryModule())

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
