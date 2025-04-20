import random
from decimal import Decimal

from flask import Flask

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases import get_statistics
from arbeitszeit_flask.database.db import Base, Database
from tests.data_generators import PlanGenerator
from tests.flask_integration.dependency_injection import get_dependency_injector


class GetStatisticsBenchmark:
    def __init__(self) -> None:
        injector = get_dependency_injector()
        app = injector.get(Flask)
        self.app_context = app.app_context()
        self.app_context.push()
        db = injector.get(Database)
        Base.metadata.drop_all(db.engine)
        Base.metadata.create_all(db.engine)
        plan_generator = injector.get(PlanGenerator)
        self.get_statistics_use_case = injector.get(get_statistics.GetStatisticsUseCase)
        random.seed()
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=True, costs=self.random_production_costs()
            )
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=False, costs=self.random_production_costs()
            )
        db.session.commit()

    def tear_down(self) -> None:
        self.app_context.pop()

    def run(self) -> None:
        self.get_statistics_use_case.get_statistics()

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
