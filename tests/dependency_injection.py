from flask_sqlalchemy import SQLAlchemy
from injector import Injector, Module, inject, provider, singleton

import arbeitszeit.repositories as interfaces
import project.models
from arbeitszeit import entities
from project import create_app
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
    def provide_account_owner_repository(
        self, repo: repositories.AccountOwnerRepository
    ) -> interfaces.AccountOwnerRepository:
        return repo

    @provider
    @singleton
    def provide_sqlalchemy(self) -> SQLAlchemy:
        db = SQLAlchemy(model_class=project.models.db.Model)
        config = {
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
        app = create_app(config=config, db=db)
        with app.app_context():
            db.create_all()
        app.app_context().push()
        return db


def injection_test(original_test):
    injector = Injector(RepositoryModule())

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
