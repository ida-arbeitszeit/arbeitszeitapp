from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummaryService
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.use_cases.dependency_injection import get_dependency_injector
from tests.use_cases.repositories import CompanyRepository


class PlanSummaryServiceTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.service = self.injector.get(PlanSummaryService)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.plan = self.plan_generator.create_plan()
        self.company_repository = self.injector.get(CompanyRepository)
        self.planner = (
            self.company_repository.get_companies().with_id(self.plan.planner).first()
        )
        assert self.planner
        self.summary = self.service.get_summary_from_plan(self.plan)
        self.payout_use_case = self.injector.get(UpdatePlansAndPayout)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_correct_planner_id_is_shown(self):
        self.assertEqual(self.summary.plan_id, self.plan.id)

    def test_that_correct_planner_name_is_shown(self):
        self.assertEqual(self.summary.planner_name, self.planner.name)

    def test_that_correct_active_status_is_shown_when_plan_is_active(self):
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        assert plan.is_active
        summary = self.service.get_summary_from_plan(plan)
        self.assertTrue(summary.is_active)

    def test_that_correct_production_costs_are_shown(self):
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            )
        )
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.means_cost, Decimal(1))
        self.assertEqual(summary.labour_cost, Decimal(2))
        self.assertEqual(summary.resources_cost, Decimal(3))

    def test_that_correct_price_per_unit_of_zero_is_shown_when_plan_is_public_service(
        self,
    ):
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.price_per_unit, Decimal(0))

    def test_that_correct_price_per_unit_is_shown_when_plan_is_productive(self):
        plan = self.plan_generator.create_plan(
            is_public_service=False,
            amount=2,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.price_per_unit, Decimal(3))

    def test_that_correct_product_name_is_shown(self):
        self.assertEqual(self.summary.product_name, self.plan.prd_name)

    def test_that_correct_product_description_is_shown(self):
        self.assertEqual(self.summary.description, self.plan.description)

    def test_that_correct_product_unit_is_shown(self):
        self.assertEqual(self.summary.production_unit, self.plan.prd_unit)

    def test_that_correct_amount_is_shown(self):
        plan = self.plan_generator.create_plan(amount=123)
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.amount, 123)

    def test_that_correct_public_service_is_shown(self):
        plan = self.plan_generator.create_plan(is_public_service=True)
        summary = self.service.get_summary_from_plan(plan)
        self.assertTrue(summary.is_public_service)

    def test_that_correct_availability_is_shown(self):
        plan = self.plan_generator.create_plan()
        assert plan.is_available
        summary = self.service.get_summary_from_plan(plan)
        self.assertTrue(summary.is_available)

    def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(self):
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=None
        )
        summary = self.service.get_summary_from_plan(plan)
        self.assertFalse(summary.is_cooperating)
        self.assertIsNone(summary.cooperation)

    def test_that_correct_cooperation_is_shown(self):
        coop = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=coop
        )
        summary = self.service.get_summary_from_plan(plan)
        self.assertTrue(summary.is_cooperating)
        self.assertEqual(summary.cooperation, coop.id)

    def test_that_zero_active_days_is_shown_if_plan_is_not_active_yet(self):
        plan = self.plan_generator.create_plan(activation_date=None)
        self.payout_use_case()
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.active_days, 0)

    def test_that_zero_active_days_is_shown_if_plan_is_active_since_less_than_one_day(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now()
        )
        self.payout_use_case()
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.active_days, 0)

    def test_that_one_active_days_is_shown_if_plan_is_active_since_25_hours(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_25_hours()
        )
        self.payout_use_case()
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.active_days, 1)

    def test_that_a_plans_timeframe_is_shown_as_active_days_if_plan_is_expired(
        self,
    ):
        timeframe = 7
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_ten_days(),
            timeframe=timeframe,
        )
        self.payout_use_case()
        summary = self.service.get_summary_from_plan(plan)
        self.assertEqual(summary.active_days, timeframe)

    def test_that_creation_date_is_shown(self):
        self.assertEqual(self.summary.creation_date, self.plan.plan_creation_date)

    def test_that_approval_date_is_shown_if_it_exists(self):
        assert self.plan.approval_date
        self.assertEqual(self.summary.approval_date, self.plan.approval_date)

    def test_that_expiration_date_is_shown_if_it_exists(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(), timeframe=5
        )
        self.payout_use_case()
        assert plan.expiration_date
        summary = self.service.get_summary_from_plan(plan)
        self.assertTrue(summary.expiration_date)
