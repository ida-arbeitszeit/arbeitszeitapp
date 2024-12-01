from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.use_cases import show_r_account_details
from arbeitszeit_flask.database.models import Base
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector


class ShowRAccountDetailsBenchmark:
    """This measures the speed of the ShowRAccountDetailsUseCase."""

    def __init__(self) -> None:
        self.injector = get_dependency_injector()
        self.db = self.injector.get(SQLAlchemy)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        Base.metadata.drop_all(self.db.engine)
        Base.metadata.create_all(self.db.engine)
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
        self.use_case = self.injector.get(
            show_r_account_details.ShowRAccountDetailsUseCase
        )
        self.db.session.commit()
        self.db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        use_case_request = show_r_account_details.Request(company=self.company)
        self.use_case.show_details(use_case_request)
