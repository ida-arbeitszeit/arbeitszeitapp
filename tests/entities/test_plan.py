from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.records import ProductionCosts
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.use_cases.dependency_injection import get_dependency_injector


class TestPlanSalesValue(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)

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


class TestPlanExpirationDate(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_plan_has_no_expiration_date_if_plan_has_not_been_approved(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.assertIsNone(plan.expiration_date)

    def test_that_plan_has_an_expiration_date_if_plan_has_been_approved(self) -> None:
        plan = self.plan_generator.create_plan(timeframe=2, approved=True)
        self.assertIsNotNone(plan.expiration_date)

    def test_that_expiration_date_is_correctly_calculated_if_plan_expires_now(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(
            timeframe=1,
            approved=True,
        )
        expected_expiration_time = datetime(2000, 1, 2)
        assert plan.expiration_date == expected_expiration_time

    def test_that_expiration_date_is_correctly_calculated_if_plan_expires_in_the_future(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(
            timeframe=2,
            approved=True,
        )
        expected_expiration_time = datetime(2000, 1, 3)
        assert plan.expiration_date == expected_expiration_time
