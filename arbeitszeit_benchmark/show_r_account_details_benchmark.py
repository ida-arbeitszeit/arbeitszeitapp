from __future__ import annotations

from flask import Flask

from arbeitszeit.interactors import show_r_account_details
from arbeitszeit_flask.database.db import Database
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector
from tests.flask_integration.flask import drop_and_recreate_schema


class ShowRAccountDetailsBenchmark:
    """This measures the speed of the ShowRAccountDetailsInteractor."""

    def __init__(self) -> None:
        self.injector = get_dependency_injector()
        self.db = self.injector.get(Database)
        drop_and_recreate_schema(self.db.engine)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        company_generator = self.injector.get(CompanyGenerator)
        plan_generator = self.injector.get(PlanGenerator)
        consumption_generator = self.injector.get(ConsumptionGenerator)
        supply_plan = plan_generator.create_plan()
        self.company = company_generator.create_company()

        for _ in range(1000):
            plan_generator.create_plan(planner=self.company)
        for _ in range(1000):
            consumption_generator.create_resource_consumption_by_company(
                plan=supply_plan, consumer=self.company
            )
        self.interactor = self.injector.get(
            show_r_account_details.ShowRAccountDetailsInteractor
        )
        self.db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        interactor_request = show_r_account_details.Request(company=self.company)
        self.interactor.show_details(interactor_request)
