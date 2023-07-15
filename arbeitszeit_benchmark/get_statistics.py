import random
from decimal import Decimal

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import get_statistics
from tests.data_generators import PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector


class GetStatisticsBenchmark:
    def __init__(self) -> None:
        injector = get_dependency_injector()
        app = injector.get(Flask)
        self.app_context = app.app_context()
        self.app_context.push()
        db = injector.get(SQLAlchemy)
        db.drop_all()
        db.create_all()
        plan_generator = injector.get(PlanGenerator)
        self.get_statistics = injector.get(get_statistics.GetStatistics)
        random.seed()
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=True, costs=self.random_production_costs()
            )
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=False, costs=self.random_production_costs()
            )

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.get_statistics()

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
