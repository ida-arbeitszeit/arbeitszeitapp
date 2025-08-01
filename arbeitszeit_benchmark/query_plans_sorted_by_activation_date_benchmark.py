import random
from decimal import Decimal

from flask import Flask

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases import query_plans
from arbeitszeit_flask.database.db import Database
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector
from tests.flask_integration.flask import drop_and_recreate_schema


class QueryPlansSortedByActivationDateBenchmark:
    def __init__(self) -> None:
        injector = get_dependency_injector()
        db = injector.get(Database)
        with db.engine.connect() as connection:
            drop_and_recreate_schema(connection)
        app = injector.get(Flask)
        self.app_context = app.app_context()
        self.app_context.push()
        plan_generator = injector.get(PlanGenerator)
        cooperation_generator = injector.get(CooperationGenerator)
        self.query_plans = injector.get(query_plans.QueryPlans)
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
        db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.query_plans(self.request)

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
