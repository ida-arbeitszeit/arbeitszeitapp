from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.use_cases.get_company_transactions import GetCompanyTransactions
from tests.data_generators import CompanyGenerator, PlanGenerator, PurchaseGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector


class GetCompanyTransactionsBenchmark:
    """This benchmark measures the execution time of the
    GetCompanyTransactions use case where there are 1000 transactions
    in the database.
    """

    def __init__(self) -> None:
        self.injector = get_dependency_injector()
        self.db = self.injector.get(SQLAlchemy)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db.drop_all()
        self.db.create_all()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.get_company_transactions = self.injector.get(GetCompanyTransactions)
        self.buyer = self.company_generator.create_company()
        for _ in range(100):
            plan = self.plan_generator.create_plan()
            for _ in range(10):
                self.purchase_generator.create_resource_purchase_by_company(
                    buyer=self.buyer, plan=plan.id
                )

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.get_company_transactions(self.buyer)