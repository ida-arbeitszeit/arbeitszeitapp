import random
from decimal import Decimal

from arbeitszeit.injector import Injector
from arbeitszeit.interactors import query_plans
from arbeitszeit.records import ProductionCosts
from arbeitszeit_db.db import Database
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.db.base_test_case import reset_test_db
from tests.db.dependency_injection import DatabaseModule
from tests.dependency_injection import TestingModule


class QueryPlansSortedByActivationDateBenchmark:
    def __init__(self) -> None:
        self.injector = Injector([TestingModule(), DatabaseModule()])
        reset_test_db()
        self.db = self.injector.get(Database)
        self.db.engine.dispose()

        plan_generator = self.injector.get(PlanGenerator)
        cooperation_generator = self.injector.get(CooperationGenerator)
        self.query_plans = self.injector.get(query_plans.QueryPlansInteractor)
        random.seed()
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=True, costs=self.random_production_costs()
            )
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=False, costs=self.random_production_costs()
            )
        for _ in range(100):
            cooperation = cooperation_generator.create_cooperation()
            for _ in range(5):
                plan_generator.create_plan(
                    cooperation=cooperation, costs=self.random_production_costs()
                )
        self.request = query_plans.QueryPlansRequest(
            query_string=None,
            filter_category=query_plans.PlanFilter.by_product_name,
            sorting_category=query_plans.PlanSorting.by_activation,
            include_expired_plans=False,
            limit=None,
            offset=None,
        )
        self.db.session.flush()

    def tear_down(self) -> None:
        self.db.session.remove()

    def run(self) -> None:
        self.query_plans.execute(self.request)

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
