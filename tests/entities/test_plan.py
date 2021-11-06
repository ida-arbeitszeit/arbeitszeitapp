from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.entities import ProductionCosts
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector
from tests.use_cases.repositories import MetaProductRepository


class TestPlanEntity(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.meta_product_repository = self.injector.get(MetaProductRepository)

    def test_price_equals_costs_when_productive_plan_and_no_meta_product(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)), amount=10
        )
        self.assertEqual(plan.price_per_unit, Decimal(2))

    def test_price_equals_zero_when_public_plan(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
            is_public_service=True,
        )
        self.assertEqual(plan.price_per_unit, Decimal(0))

    def test_prices_of_two_associated_plans_are_equal(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan1 = self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
            amount=5,
        )

        meta_product = self.meta_product_repository.create_meta_product(
            datetime.now(), name="test", definition="test info", coordinator=company
        )
        self.meta_product_repository.add_plan_to_meta_product(plan1.id, meta_product.id)
        self.meta_product_repository.add_plan_to_meta_product(plan2.id, meta_product.id)
        self.assertEqual(plan1.price_per_unit, plan2.price_per_unit)

    def test_price_is_average_of_prices_of_cooperating_plans(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan1 = self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
            amount=10,
        )

        meta_product = self.meta_product_repository.create_meta_product(
            datetime.now(), name="test", definition="test info", coordinator=company
        )
        self.meta_product_repository.add_plan_to_meta_product(plan1.id, meta_product.id)
        self.meta_product_repository.add_plan_to_meta_product(plan2.id, meta_product.id)
        self.assertEqual(plan1.price_per_unit, Decimal("1.5"))

    def test_expected_sales_value_is_zero_for_public_plan(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        self.assertEqual(plan.expected_sales_value, Decimal(0))

    def test_expected_sales_value_equals_individual_production_costs_for_productive_plan(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)), amount=10
        )
        self.assertEqual(plan.expected_sales_value, Decimal(20))
