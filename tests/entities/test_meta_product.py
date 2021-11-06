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

    def test_price_is_zero_when_one_plan_with_price_of_zero_is_associated_with_product(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(0))
        )
        product = MetaProduct(
            id=uuid4(),
            creation_date=datetime.min,
            name="product name",
            definition="usefull info",
            coordinator=self.company_generator.create_company(),
            plans=[plan],
        )
        self.assertEqual(product.meta_price_per_unit, Decimal(0))

    def test_price_is_average_of_prices_of_associated_plans(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)), amount=10
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(1)), amount=10
        )
        plan3 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(2), Decimal(3)), amount=10
        )
        exp_price1 = Decimal("2")
        exp_price2 = Decimal("0.1")
        exp_price3 = Decimal("1.5")
        exp_average_of_prices = sum([exp_price1, exp_price2, exp_price3]) / 3
        product = MetaProduct(
            id=uuid4(),
            creation_date=datetime.min,
            name="product name",
            definition="usefull info",
            coordinator=self.company_generator.create_company(),
            plans=[plan1, plan2, plan3],
        )
        self.assertEqual(product.meta_price_per_unit, exp_average_of_prices)
