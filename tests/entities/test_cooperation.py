from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import Cooperation, ProductionCosts
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector


class TestCoopPricePerUnit(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_price_is_zero_when_no_plans_are_cooperating(self) -> None:
        cooperation = Cooperation(
            id=uuid4(),
            creation_date=datetime.min,
            name="product name",
            definition="usefull info",
            coordinator=self.company_generator.create_company(),
            plans=[],
        )
        self.assertEqual(cooperation.coop_price_per_unit, Decimal(0))

    def test_price_is_average_of_prices_of_cooperating_plans(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(50), Decimal(25), Decimal(24)), amount=1
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(1)), amount=9
        )
        # total costs are 100, there are 10 units -> price should be 10h/unit
        exp_average_of_prices = Decimal("10")
        cooperation = Cooperation(
            id=uuid4(),
            creation_date=datetime.min,
            name="product name",
            definition="usefull info",
            coordinator=self.company_generator.create_company(),
            plans=[plan1, plan2],
        )
        self.assertEqual(cooperation.coop_price_per_unit, exp_average_of_prices)
