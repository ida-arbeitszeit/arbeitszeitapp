from arbeitszeit.injector import Injector
from arbeitszeit.interactors import get_company_summary
from arbeitszeit_db.db import Database
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.db.base_test_case import reset_test_db
from tests.db.dependency_injection import DatabaseModule
from tests.dependency_injection import TestingModule


class GetCompanySummaryBenchmark:
    """This benchmark measures the performance of the
    get_company_summary interactor with a company that has made 1000
    productive consumptions and created 1000 approved plans.
    """

    def __init__(self) -> None:
        self.injector = Injector([TestingModule(), DatabaseModule()])
        reset_test_db()
        self.db = self.injector.get(Database)
        self.db.engine.dispose()

        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
        self.get_company_summary = self.injector.get(
            get_company_summary.GetCompanySummaryInteractor
        )
        self.company = self.company_generator.create_company()
        for _ in range(100):
            plan = self.plan_generator.create_plan()
            for _ in range(5):
                self.consumption_generator.create_resource_consumption_by_company(
                    consumer=self.company, plan=plan
                )
                self.consumption_generator.create_fixed_means_consumption(
                    consumer=self.company, plan=plan
                )
        for _ in range(1000):
            self.plan_generator.create_plan(planner=self.company)
        self.db.session.flush()

    def tear_down(self) -> None:
        self.db.session.remove()

    def run(self) -> None:
        self.get_company_summary.execute(self.company)
