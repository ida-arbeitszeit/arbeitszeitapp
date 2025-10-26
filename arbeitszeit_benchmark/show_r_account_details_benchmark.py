from arbeitszeit.injector import Injector
from arbeitszeit.interactors import show_r_account_details
from arbeitszeit_db.db import Database
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.db.base_test_case import reset_test_db
from tests.db.dependency_injection import DatabaseModule
from tests.dependency_injection import TestingModule


class ShowRAccountDetailsBenchmark:
    """This measures the speed of the ShowRAccountDetailsInteractor."""

    def __init__(self) -> None:
        self.injector = Injector([TestingModule(), DatabaseModule()])
        reset_test_db()
        self.db = self.injector.get(Database)
        self.db.engine.dispose()

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
        self.db.session.remove()

    def run(self) -> None:
        interactor_request = show_r_account_details.Request(company=self.company)
        self.interactor.show_details(interactor_request)
