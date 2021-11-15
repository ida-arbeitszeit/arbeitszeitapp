from decimal import Decimal
from unittest import TestCase

from arbeitszeit.entities import ProductionCosts
from tests.data_generators import PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector


class TestPlanEntity(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_price_equals_costs_when_productive_plan_and_no_cooperation(self) -> None:
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
