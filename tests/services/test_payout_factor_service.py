from decimal import Decimal

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.payout_factor import PayoutFactorService
from tests.use_cases.base_test_case import BaseTestCase


class CalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PayoutFactorService)

    def test_that_payout_factor_is_zero_if_no_plans_exist(self):
        pf = self.service.calculate_payout_factor()
        self.assertEqual(pf, 0)

    def test_that_payout_factor_is_negative_with_one_public_plan_that_includes_p_or_r(
        self,
    ):
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        pf = self.service.calculate_payout_factor()
        self.assertTrue(pf < 0)

    def test_that_payout_factor_is_zero_with_one_public_plan_that_does_not_includes_p_or_r(
        self,
    ):
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor()
        self.assertEqual(pf, 0)

    def test_that_payout_factor_is_zero_when_productive_labour_equals_sum_of_public_p_and_r(
        self,
    ):
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(20), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor()
        self.assertEqual(pf, 0)

    def test_that_payout_factor_is_positive_when_productive_labour_surpasses_sum_of_public_p_and_r(
        self,
    ):
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(21), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor()
        self.assertTrue(pf > 0)

    def test_that_payout_factor_is_negative_when_sum_of_public_p_and_r_surpasses_productive_labour(
        self,
    ):
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(19), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor()
        self.assertTrue(pf < 0)

    def test_that_correct_payout_factor_gets_calculated(self):
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
        pf = self.service.calculate_payout_factor()
        expected_payout_factor = Decimal((A - (Po + Ro)) / (A + Ao))
        self.assertAlmostEqual(pf, expected_payout_factor)
