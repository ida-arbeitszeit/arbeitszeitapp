from decimal import Decimal

from arbeitszeit import records
from arbeitszeit.records import ProductionCosts
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class PlanTestBase(BaseTestCase):
    def create_plan_record(
        self,
        is_public_service: bool = False,
        costs: ProductionCosts = ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
        amount: int = 5,
        approved: bool = False,
        timeframe: int = 365,
    ) -> records.Plan:
        plan_id = self.plan_generator.create_plan(
            amount=amount,
            is_public_service=is_public_service,
            costs=costs,
            approved=approved,
            timeframe=timeframe,
        )
        plan = self.database_gateway.get_plans().with_id(plan_id).first()
        assert plan
        return plan


class TestPlanSalesValue(PlanTestBase):
    def test_expected_sales_value_is_zero_for_public_plan(self) -> None:
        plan = self.create_plan_record(is_public_service=True)
        self.assertEqual(plan.expected_sales_value, Decimal(0))

    def test_expected_sales_value_equals_individual_production_costs_for_productive_plan(
        self,
    ) -> None:
        plan = self.create_plan_record(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)), amount=10
        )
        self.assertEqual(plan.expected_sales_value, Decimal(20))


class TestPlanExpirationDate(PlanTestBase):
    def test_that_plan_has_no_expiration_date_if_plan_has_not_been_approved(
        self,
    ) -> None:
        plan = self.create_plan_record(approved=False)
        self.assertIsNone(plan.expiration_date)

    def test_that_plan_has_an_expiration_date_if_plan_has_been_approved(self) -> None:
        plan = self.create_plan_record(timeframe=2, approved=True)
        self.assertIsNotNone(plan.expiration_date)

    def test_that_expiration_date_is_correctly_calculated_if_plan_expires_now(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.create_plan_record(
            timeframe=1,
            approved=True,
        )
        expected_expiration_time = datetime_utc(2000, 1, 2)
        assert plan.expiration_date == expected_expiration_time

    def test_that_expiration_date_is_correctly_calculated_if_plan_expires_in_the_future(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.create_plan_record(
            timeframe=2,
            approved=True,
        )
        expected_expiration_time = datetime_utc(2000, 1, 3)
        assert plan.expiration_date == expected_expiration_time
