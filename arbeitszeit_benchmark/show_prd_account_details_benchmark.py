from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.use_cases.show_prd_account_details import ShowPRDAccountDetailsUseCase
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector


class ShowPrdAccountDetailsBenchmark:
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
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
        self.email = "test@test.test"
        self.password = "test1234123"
        self.seller = self.company_generator.create_company(
            confirmed=True, email=self.email, password=self.password
        )
        plan = self.plan_generator.create_plan(planner=self.seller)
        for _ in range(1000):
            self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        self.use_case = self.injector.get(ShowPRDAccountDetailsUseCase)
        self.db.session.commit()
        self.db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.use_case(self.seller)
