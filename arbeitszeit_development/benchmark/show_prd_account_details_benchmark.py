from arbeitszeit.injector import Injector
from arbeitszeit.interactors import show_prd_account_details
from arbeitszeit_db.db import Database
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.db.base_test_case import reset_test_db
from tests.db.dependency_injection import DatabaseModule
from tests.dependency_injection import TestingModule


class ShowPrdAccountDetailsBenchmark:
    """This benchmark measures the execution time of the
    ShowPRDAccountDetailsInteractor where there are 1000 transactions
    in the database.
    """

    def __init__(self) -> None:
        self.injector = Injector([TestingModule(), DatabaseModule()])
        reset_test_db()
        self.db = self.injector.get(Database)
        self.db.engine.dispose()

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
        self.db.session.remove()

    def run(self) -> None:
        interactor_request = show_prd_account_details.Request(company_id=self.seller)
        self.interactor.show_details(interactor_request)
