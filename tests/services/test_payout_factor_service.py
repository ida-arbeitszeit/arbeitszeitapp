from datetime import datetime, timedelta
from decimal import Decimal

from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.records import ProductionCosts
from tests.use_cases.base_test_case import BaseTestCase


class CalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PayoutFactorService)

    def test_that_payout_factor_is_one_if_no_plans_exist(self) -> None:
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertEqual(pf, 1)

    def test_that_payout_factor_is_negative_with_one_public_plan_that_includes_p_or_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertTrue(pf < 0)

    def test_that_payout_factor_is_zero_with_one_public_plan_that_does_not_includes_p_or_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertEqual(pf, 0)

    def test_that_payout_factor_is_zero_when_productive_labour_equals_sum_of_public_p_and_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(20), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertEqual(pf, 0)

    def test_that_payout_factor_is_positive_when_productive_labour_surpasses_sum_of_public_p_and_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(21), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertTrue(pf > 0)

    def test_that_payout_factor_is_negative_when_sum_of_public_p_and_r_surpasses_productive_labour(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(19), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertTrue(pf < 0)

    def test_that_correct_payout_factor_gets_calculated(self) -> None:
        A = 10
        Po = 10
        Ro = 10
        Ao = 10

        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(Ao), Decimal(Ro), Decimal(Po)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(A), Decimal(10), Decimal(10)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        expected_payout_factor = Decimal((A - (Po + Ro)) / (A + Ao))
        self.assertAlmostEqual(pf, expected_payout_factor)

    def test_that_payout_factor_gets_calculated_based_on_supplied_timestamp(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            timeframe=10,
        )
        self.datetime_service.advance_time(timedelta(days=5))
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(10),
                resource_cost=Decimal(0),
            ),
            timeframe=10,
        )
        assert self.service.calculate_payout_factor(datetime(2000, 1, 2)) == Decimal(1)
        assert self.service.calculate_payout_factor(datetime(2000, 1, 6)) == Decimal(0)
