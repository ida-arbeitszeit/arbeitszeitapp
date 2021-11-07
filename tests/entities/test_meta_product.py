from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import MetaProduct, ProductionCosts
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector


class TestMetaPricePerUnit(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_price_is_zero_when_no_plans_are_associated_with_product(self) -> None:
        product = MetaProduct(
            id=uuid4(),
            creation_date=datetime.min,
            name="product name",
            definition="usefull info",
            coordinator=self.company_generator.create_company(),
            plans=[],
        )
        self.assertEqual(product.meta_price_per_unit, Decimal(0))

    def test_price_is_average_of_prices_of_associated_plans(
        self,
    ) -> None:
        # total costs are 100, there are 10 units -> price should be 10h/unit
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(50), Decimal(25), Decimal(24)), amount=1
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(1)), amount=9
        )
        exp_average_of_prices = Decimal("10")
        product = MetaProduct(
            id=uuid4(),
            creation_date=datetime.min,
            name="product name",
            definition="usefull info",
            coordinator=self.company_generator.create_company(),
            plans=[plan1, plan2],
        )
        self.assertEqual(product.meta_price_per_unit, exp_average_of_prices)
