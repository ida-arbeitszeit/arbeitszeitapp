from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.price_calculator import PriceCalculator
from tests.interactors.base_test_case import BaseTestCase


class PriceCalculatorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.calculator = self.injector.get(PriceCalculator)

    def test_that_service_returns_none_for_noncooperating_public_plan(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        price = self.calculator.calculate_cooperative_price(plan)
        assert price is None

    def test_that_service_returns_none_for_noncooperating_productive_plan(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=False)
        price = self.calculator.calculate_cooperative_price(plan)
        assert price is None

    def test_that_price_is_zero_when_all_plans_in_cooperation_produce_zero_units(
        self,
    ) -> None:
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
            amount=0,
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
            amount=0,
        )
        self.cooperation_generator.create_cooperation(
            plans=[plan_1, plan_2],
        )
        price = self.calculator.calculate_cooperative_price(plan_1)
        assert price is not None
        assert price == Decimal(0)

    @parameterized.expand(
        [
            (Decimal(10),),
            (Decimal(20),),
        ]
    )
    def test_that_price_of_plan_that_is_sole_cooperation_member_equals_its_own_costs(
        self,
        costs: Decimal,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(costs, Decimal(0), Decimal(0)),
            amount=1,
        )
        self.cooperation_generator.create_cooperation(plans=[plan])
        price = self.calculator.calculate_cooperative_price(plan)
        assert price is not None
        self.assertAlmostEqual(price, costs)

    @parameterized.expand(
        [
            (Decimal(10), Decimal(20), Decimal(15)),
            (Decimal(20), Decimal(30), Decimal(25)),
        ]
    )
    def test_that_cooperative_price_for_two_companies_is_average_of_costs(
        self,
        costs_1: Decimal,
        costs_2: Decimal,
        expected_price: Decimal,
    ) -> None:
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_1, Decimal(0), Decimal(0)),
            amount=1,
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_2, Decimal(0), Decimal(0)),
            amount=1,
        )
        self.cooperation_generator.create_cooperation(
            plans=[plan_1, plan_2],
        )
        price = self.calculator.calculate_cooperative_price(plan_1)
        assert price is not None
        self.assertAlmostEqual(price, expected_price)

    @parameterized.expand(
        [
            (Decimal(10), Decimal(20), Decimal(30), Decimal(20)),
            (Decimal(20), Decimal(30), Decimal(40), Decimal(30)),
        ]
    )
    def test_that_cooperative_price_for_three_companies_is_average_of_costs(
        self,
        costs_1: Decimal,
        costs_2: Decimal,
        costs_3: Decimal,
        expected_price: Decimal,
    ) -> None:
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_1, Decimal(0), Decimal(0)),
            amount=1,
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_2, Decimal(0), Decimal(0)),
            amount=1,
        )
        plan_3 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_3, Decimal(0), Decimal(0)),
            amount=1,
        )
        self.cooperation_generator.create_cooperation(
            plans=[plan_1, plan_2, plan_3],
        )
        price = self.calculator.calculate_cooperative_price(plan_1)
        assert price is not None
        self.assertAlmostEqual(price, expected_price)

    @parameterized.expand(
        [
            (Decimal(1), 1, Decimal(3), 1, Decimal(2)),
            (Decimal(1), 38, Decimal(3), 1, Decimal(2)),
            (Decimal(1), 1, Decimal(3), 72, Decimal(2)),
        ]
    )
    def test_that_cooperative_price_for_two_companies_is_average_of_costs_independent_of_duration(
        self,
        costs_1: Decimal,
        duration_1: int,
        costs_2: Decimal,
        duration_2: int,
        expected_price: Decimal,
    ) -> None:
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_1, Decimal(0), Decimal(0)),
            amount=1,
            timeframe=duration_1,
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(costs_2, Decimal(0), Decimal(0)),
            amount=1,
            timeframe=duration_2,
        )
        self.cooperation_generator.create_cooperation(
            plans=[plan_1, plan_2],
        )
        price = self.calculator.calculate_cooperative_price(plan_1)
        assert price is not None
        self.assertAlmostEqual(price, expected_price)
