import random
from decimal import Decimal

from flask import Flask

from arbeitszeit.interactors import get_statistics
from arbeitszeit.records import ProductionCosts
from arbeitszeit_db.db import Database
from tests.data_generators import PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector
from tests.flask_integration.flask import drop_and_recreate_schema


class GetStatisticsBenchmark:
    def __init__(self) -> None:
        injector = get_dependency_injector()
        db = injector.get(Database)
        drop_and_recreate_schema(db.engine)
        app = injector.get(Flask)
        self.app_context = app.app_context()
        self.app_context.push()
        plan_generator = injector.get(PlanGenerator)
        self.get_statistics_interactor = injector.get(
            get_statistics.GetStatisticsInteractor
        )
        random.seed()
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=True, costs=self.random_production_costs()
            )
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=False, costs=self.random_production_costs()
            )
        db.session.flush()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.get_statistics_interactor.get_statistics()

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
