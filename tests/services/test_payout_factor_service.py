from datetime import timedelta
from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.payout_factor import PayoutFactorService
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class PayoutFactorServiceCalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PayoutFactorService)

    def test_that_payout_factor_is_1_if_no_plans_exist(self) -> None:
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        assert pf == 1

    def test_that_payout_factor_is_1_if_there_is_only_one_public_plan_without_costs(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts.zero(),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        assert pf == 1

    @parameterized.expand(
        [
            (Decimal(1), Decimal(0), Decimal(1)),
            (Decimal(1), Decimal(1), Decimal(0)),
            (Decimal(1), Decimal(0), Decimal(0)),
            (Decimal(1), Decimal(1), Decimal(1)),
            (Decimal(0), Decimal(0), Decimal(1)),
            (Decimal(0), Decimal(1), Decimal(0)),
            (Decimal(0), Decimal(1), Decimal(1)),
        ]
    )
    def test_that_payout_factor_is_0_if_there_is_only_one_public_plan_with_costs(
        self,
        public_a: Decimal,
        public_p: Decimal,
        public_r: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(public_a, public_p, public_r),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        assert pf == 0

    def test_that_payout_factor_is_0_when_productive_labour_equals_sum_of_public_p_and_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(20), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        assert pf == 0

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
        assert pf > 0

    def test_that_payout_factor_is_zero_when_sum_of_public_p_and_r_surpasses_productive_labour(
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
        assert pf == 0

    @parameterized.expand(
        [
            (Decimal(10), Decimal(10), Decimal(10), Decimal(10), Decimal(0)),
            (Decimal(20), Decimal(10), Decimal(10), Decimal(10), Decimal(0)),
            (Decimal(30), Decimal(10), Decimal(10), Decimal(10), Decimal(0.25)),
            (Decimal(30), Decimal(0), Decimal(0), Decimal(0), Decimal(1)),
        ]
    )
    def test_that_expected_payout_factor_gets_calculated(
        self,
        productive_a: Decimal,
        public_a: Decimal,
        public_p: Decimal,
        public_r: Decimal,
        expected_payout_factor: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(public_a, public_r, public_p),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(productive_a, Decimal(10), Decimal(10)),
        )
        pf = self.service.calculate_payout_factor(self.datetime_service.now())
        self.assertAlmostEqual(pf, expected_payout_factor)

    def test_that_payout_factor_gets_calculated_based_on_supplied_timestamp(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
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
        assert self.service.calculate_payout_factor(
            datetime_utc(2000, 1, 2)
        ) == Decimal(1)
        assert self.service.calculate_payout_factor(
            datetime_utc(2000, 1, 6)
        ) == Decimal(0)
