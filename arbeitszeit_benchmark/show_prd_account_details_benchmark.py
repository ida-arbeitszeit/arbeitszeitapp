from __future__ import annotations

from flask import Flask

from arbeitszeit.interactors import show_prd_account_details
from arbeitszeit_flask.database.db import Database
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector
from tests.flask_integration.flask import drop_and_recreate_schema


class ShowPrdAccountDetailsBenchmark:
    """This benchmark measures the execution time of the
    ShowPRDAccountDetailsInteractor where there are 1000 transactions
    in the database.
    """

    def __init__(self) -> None:
        self.injector = get_dependency_injector()
        self.db = self.injector.get(Database)
        drop_and_recreate_schema(self.db.engine)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
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
        self.interactor = self.injector.get(
            show_prd_account_details.ShowPRDAccountDetailsInteractor
        )
        self.db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        interactor_request = show_prd_account_details.Request(company_id=self.seller)
        self.interactor.show_details(interactor_request)
