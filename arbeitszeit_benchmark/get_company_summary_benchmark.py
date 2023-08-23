from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.use_cases import get_company_summary
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector


class GetCompanySummaryBenchmark:
    """This benchmark measures the performance of the
    get_company_summary use case with a company that has made 1000
    productive consumptions and created 1000 approved plans.
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
        self.get_company_summary = self.injector.get(
            get_company_summary.GetCompanySummary
        )
        self.company = self.company_generator.create_company()
        for _ in range(100):
            plan = self.plan_generator.create_plan()
            for _ in range(5):
                self.consumption_generator.create_resource_consumption_by_company(
                    consumer=self.company, plan=plan.id
                )
                self.consumption_generator.create_fixed_means_consumption(
                    consumer=self.company, plan=plan.id
                )
        for _ in range(1000):
            self.plan_generator.create_plan(planner=self.company)
        self.db.session.commit()
        self.db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.get_company_summary(self.company)
