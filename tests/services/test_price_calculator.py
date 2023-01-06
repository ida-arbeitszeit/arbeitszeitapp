from dataclasses import dataclass
from decimal import Decimal
from unittest import TestCase

from pytest import approx

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.price_calculator import PriceCalculator
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector


class TestPriceCalculator(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.price_calculator = self.injector.get(PriceCalculator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_that_two_productive_plans_with_different_timeframes_return_correct_coop_price_1(
        self,
    ):
        cooperation = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(
            cooperation=cooperation,
            costs=ProductionCosts(Decimal(10), Decimal(0), Decimal(0)),
            amount=10,
            timeframe=10,
        )  # 1 piece/day, 1 costs/day
        plan = self.plan_generator.create_plan(
            cooperation=cooperation,
            costs=ProductionCosts(Decimal(20), Decimal(0), Decimal(0)),
            amount=5,
            timeframe=1,
        )  # 5 piece/day, 20 costs/day
        price = self.price_calculator.calculate_cooperative_price(plan)
        self.assertEqual(
            price, Decimal(3.5)
        )  # coop price = 21 costs/day / 6 pieces/day = 3,5h/piece

    def test_that_two_productive_plans_with_different_timeframes_return_correct_coop_price_2(
        self,
    ):
        cooperation = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(
            cooperation=cooperation,
            costs=ProductionCosts(Decimal(300), Decimal(10), Decimal(0)),
            amount=20,
            timeframe=90,
        )
        plan = self.plan_generator.create_plan(
            cooperation=cooperation,
            costs=ProductionCosts(Decimal(25), Decimal(0), Decimal(0)),
            amount=5,
            timeframe=45,
        )
        price = self.price_calculator.calculate_cooperative_price(plan)
        self.assertEqual(
            price, Decimal(12)
        )  # coop price = 4h/day / 0,3333 pieces/day = 12h/piece

    def test_that_cooperative_prices_are_calculated_by_averaging_plan_prices(
        self,
    ) -> None:
        @dataclass
        class TestExample:
            plan_a_costs: Decimal
            plan_b_costs: Decimal
            expected_cooperative_costs: Decimal

        examples = [
            TestExample(
                plan_a_costs=Decimal(5),
                plan_b_costs=Decimal(15),
                expected_cooperative_costs=Decimal(10),
            ),
            TestExample(
                plan_a_costs=Decimal(3),
                plan_b_costs=Decimal(5),
                expected_cooperative_costs=Decimal(4),
            ),
        ]
        for example in examples:
            coop = self.cooperation_generator.create_cooperation()
            self.plan_generator.create_plan(
                cooperation=coop,
                costs=self.create_production_costs(total_costs=example.plan_a_costs),
                amount=1,
            )
            plan = self.plan_generator.create_plan(
                cooperation=coop,
                costs=self.create_production_costs(total_costs=example.plan_b_costs),
                amount=1,
            )
            assert self.price_calculator.calculate_cooperative_price(plan) == approx(
                example.expected_cooperative_costs
            )

    def test_that_indiviual_price_is_calculated_properly(self) -> None:
        @dataclass
        class TestExample:
            total_costs: Decimal
            amount: int
            expected_costs: Decimal

        examples = [
            TestExample(total_costs=Decimal(1), amount=1, expected_costs=Decimal(1)),
            TestExample(total_costs=Decimal(3), amount=1, expected_costs=Decimal(3)),
            TestExample(total_costs=Decimal(3), amount=3, expected_costs=Decimal(1)),
        ]
        for example in examples:
            plan = self.plan_generator.create_plan(
                costs=self.create_production_costs(total_costs=example.total_costs),
                amount=example.amount,
            )
            assert self.price_calculator.calculate_individual_price(plan) == approx(
                example.expected_costs
            )

    def test_that_individual_price_for_public_plan_is_0(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=self.create_production_costs(total_costs=Decimal(10)),
            amount=1,
            is_public_service=True,
        )
        assert self.price_calculator.calculate_individual_price(plan) == Decimal(0)

    def test_that_cooperative_price_for_public_plan_is_0(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=self.create_production_costs(total_costs=Decimal(10)),
            amount=1,
            is_public_service=True,
        )
        assert self.price_calculator.calculate_cooperative_price(plan) == Decimal(0)

    def create_production_costs(
        self, total_costs: Decimal = Decimal(1)
    ) -> ProductionCosts:
        return ProductionCosts(total_costs / 3, total_costs / 3, total_costs / 3)
