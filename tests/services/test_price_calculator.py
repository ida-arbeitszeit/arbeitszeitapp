from decimal import Decimal
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.price_calculator import PriceCalculator
from tests.interactors.base_test_case import BaseTestCase


class PriceCalculatorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PriceCalculator)

    def test_price_is_zero_for_nonexisting_plan(self) -> None:
        assert self.service.calculate_price(uuid4()) == 0

    def test_price_is_zero_for_public_plan(self) -> None:
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
        )
        price = self.service.calculate_price(plan)
        assert price == 0

    @parameterized.expand(
        [
            (
                Decimal(0),
                0,
            ),
            (
                Decimal(10),
                0,
            ),
            (
                Decimal(10),
                5,
            ),
            (Decimal(0), 2),
        ]
    )
    def test_price_equals_cost_per_unit_if_productive_plan_is_not_cooperating(
        self,
        costs: Decimal,
        units: int,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(costs / 3, costs / 3, costs / 3),
            amount=units,
            is_public_service=False,
            cooperation=None,
        )
        price = self.service.calculate_price(plan)
        assert price == (costs / units if units else Decimal(0))

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
        price1 = self.service.calculate_price(plan_1)
        price2 = self.service.calculate_price(plan_2)
        assert price1 == price2 == 0

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
        price = self.service.calculate_price(plan)
        assert price == costs

    @parameterized.expand(
        [
            (Decimal(10), Decimal(20)),
            (Decimal(20), Decimal(30)),
        ]
    )
    def test_that_cooperative_price_for_two_companies_is_average_of_costs(
        self,
        costs_1: Decimal,
        costs_2: Decimal,
    ) -> None:
        expected_price = (costs_1 + costs_2) / 2
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
        price1 = self.service.calculate_price(plan_1)
        price2 = self.service.calculate_price(plan_2)
        assert price1 == price2 == expected_price

    @parameterized.expand(
        [
            (Decimal(10), Decimal(20), Decimal(30)),
            (Decimal(20), Decimal(30), Decimal(40)),
        ]
    )
    def test_that_cooperative_price_for_three_companies_is_average_of_costs(
        self,
        costs_1: Decimal,
        costs_2: Decimal,
        costs_3: Decimal,
    ) -> None:
        expected_price = (costs_1 + costs_2 + costs_3) / 3
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
        price1 = self.service._calculate_cooperative_price(plan_1)
        price2 = self.service._calculate_cooperative_price(plan_2)
        price3 = self.service._calculate_cooperative_price(plan_3)
        assert price1 == price2 == price3 == expected_price

    @parameterized.expand(
        [
            (Decimal(1), 1, Decimal(3), 1),
            (Decimal(1), 38, Decimal(3), 1),
            (Decimal(1), 1, Decimal(3), 72),
        ]
    )
    def test_that_cooperative_price_for_two_companies_is_average_of_costs_independent_of_duration(
        self,
        costs_1: Decimal,
        duration_1: int,
        costs_2: Decimal,
        duration_2: int,
    ) -> None:
        expected_price = (costs_1 + costs_2) / 2
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
        price1 = self.service._calculate_cooperative_price(plan_1)
        price2 = self.service._calculate_cooperative_price(plan_2)
        assert price1 == price2 == expected_price
