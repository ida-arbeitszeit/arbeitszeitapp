from decimal import Decimal
from unittest import TestCase

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.price_calculator import calculate_price
from tests.data_generators import PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector


class TestPriceCalculator(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_empty_list_of_plans_raises_assertion_error(self):
        with self.assertRaises(AssertionError):
            calculate_price([])

    def test_that_one_productive_plan_returns_individual_costs_per_unit_as_price(self):
        plan = self.plan_generator.create_plan()
        price = calculate_price([plan])
        self.assertEqual(price, plan.production_costs.total_cost() / plan.prd_amount)

    def test_that_one_public_plan_returns_zero_as_price(self):
        plan = self.plan_generator.create_plan(is_public_service=True)
        price = calculate_price([plan])
        self.assertEqual(price, 0)

    def test_that_one_public_and_one_productive_plan_raises_assertion_error(self):
        plan1 = self.plan_generator.create_plan(is_public_service=True)
        plan2 = self.plan_generator.create_plan(is_public_service=False)
        with self.assertRaises(AssertionError):
            calculate_price([plan1, plan2])

    def test_that_two_productive_plans_return_correct_coop_price(self):
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(6)), amount=10
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)), amount=6
        )
        price = calculate_price([plan1, plan2])
        self.assertEqual(round(price, 4), Decimal(0.8125))  # 13/16

    def test_that_two_productive_plans_with_different_timeframes_return_correct_coop_price_1(
        self,
    ):
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(0), Decimal(0)),
            amount=10,
            timeframe=10,
        )  # 1 piece/day, 1 costs/day
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(20), Decimal(0), Decimal(0)),
            amount=5,
            timeframe=1,
        )  # 5 piece/day, 20 costs/day
        price = calculate_price([plan1, plan2])
        self.assertEqual(
            price, Decimal(3.5)
        )  # coop price = 21 costs/day / 6 pieces/day = 3,5h/piece

    def test_that_two_productive_plans_with_different_timeframes_return_correct_coop_price_2(
        self,
    ):
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(300), Decimal(10), Decimal(0)),
            amount=20,
            timeframe=90,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(25), Decimal(0), Decimal(0)),
            amount=5,
            timeframe=45,
        )
        price = calculate_price([plan1, plan2])
        self.assertEqual(
            price, Decimal(12)
        )  # coop price = 4h/day / 0,3333 pieces/day = 12h/piece
