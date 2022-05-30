from datetime import datetime
from decimal import Decimal
from typing import Callable
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases import (
    GetPlanSummaryMember,
    PlanSummaryResponse,
    PlanSummarySuccess,
)
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.use_case = self.injector.get(GetPlanSummaryMember)
        self.payout_use_case = self.injector.get(UpdatePlansAndPayout)
        self.company = self.company_generator.create_company()

    def test_that_correct_planner_name_is_shown(self):
        plan = self.plan_generator.create_plan(planner=self.company)
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.planner_name == plan.planner.name)

    def test_that_correct_planner_id_is_shown(self):
        plan = self.plan_generator.create_plan(planner=self.company)
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.planner_id == plan.planner.id)

    def test_that_correct_active_status_is_shown_when_plan_is_inactive(self):
        plan = self.plan_generator.create_plan(activation_date=None)
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.is_active == False)

    def test_that_correct_active_status_is_shown_when_plan_is_active(self):
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.is_active == True)

    def test_that_correct_production_costs_are_shown(self):
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            )
        )
        summary = self.use_case(plan.id)
        self.assert_success(
            summary,
            lambda s: all(
                [
                    s.means_cost == Decimal(1),
                    s.labour_cost == Decimal(2),
                    s.resources_cost == Decimal(3),
                ]
            ),
        )

    def test_that_correct_price_per_unit_is_shown_when_plan_is_public_service(self):
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.price_per_unit == Decimal(0))

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
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.price_per_unit == Decimal(3))

    def test_that_correct_product_name_is_shown(self):
        plan = self.plan_generator.create_plan(product_name="test product")
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.product_name == "test product")

    def test_that_correct_product_description_is_shown(self):
        plan = self.plan_generator.create_plan(description="test description")
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.description == "test description")

    def test_that_correct_product_unit_is_shown(self):
        plan = self.plan_generator.create_plan(production_unit="test unit")
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.production_unit == "test unit")

    def test_that_correct_amount_is_shown(self):
        plan = self.plan_generator.create_plan(amount=123)
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.amount == 123)

    def test_that_correct_public_service_is_shown(self):
        plan = self.plan_generator.create_plan(is_public_service=True)
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.is_public_service == True)

    def test_that_none_is_returned_when_plan_does_not_exist(self) -> None:
        self.assertIsNone(self.use_case(uuid4()))

    def test_that_correct_availability_is_shown(self):
        plan = self.plan_generator.create_plan()
        assert plan.is_available
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.is_available == True)

    def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(self):
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=None
        )
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.is_cooperating == False)
        self.assert_success(summary, lambda s: s.cooperation is None)

    def test_that_correct_cooperation_is_shown(self):
        coop_generator = self.injector.get(CooperationGenerator)
        coop = coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=coop
        )
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.is_cooperating == True)
        self.assert_success(summary, lambda s: s.cooperation == coop.id)

    def test_that_zero_active_days_is_shown_if_plan_is_not_active_yet(self):
        plan = self.plan_generator.create_plan(activation_date=None)
        self.payout_use_case()
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.active_days == 0)

    def test_that_zero_active_days_is_shown_if_plan_is_active_since_less_than_one_day(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now()
        )
        self.payout_use_case()
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.active_days == 0)

    def test_that_one_active_days_is_shown_if_plan_is_active_since_25_hours(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_25_hours()
        )
        self.payout_use_case()
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.active_days == 1)

    def test_that_a_plans_timeframe_is_shown_as_active_days_if_plan_is_expired(
        self,
    ):
        timeframe = 7
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_ten_days(),
            timeframe=timeframe,
        )
        self.payout_use_case()
        summary = self.use_case(plan.id)
        self.assert_success(summary, lambda s: s.active_days == timeframe)

    def assert_success(
        self,
        response: PlanSummaryResponse,
        assertion: Callable[[BusinessPlanSummary], bool],
    ) -> None:
        assert isinstance(response, PlanSummarySuccess)
        assert isinstance(response.plan_summary, BusinessPlanSummary)
        assert assertion(response.plan_summary)
