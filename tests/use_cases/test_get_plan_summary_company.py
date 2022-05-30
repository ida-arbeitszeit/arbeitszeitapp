from datetime import datetime
from decimal import Decimal
from typing import Callable, Union
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases import GetPlanSummaryCompany
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class Tests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.get_plan_summary_company = self.injector.get(GetPlanSummaryCompany)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.payout_use_case = self.injector.get(UpdatePlansAndPayout)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_current_user_is_correctly_shown_as_planner(self):
        planner_and_current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner_and_current_user)
        response = self.get_plan_summary_company(plan.id, planner_and_current_user.id)
        assert isinstance(response, GetPlanSummaryCompany.Success)
        assert response.current_user_is_planner

    def test_that_current_user_is_correctly_shown_as_non_planner(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert isinstance(response, GetPlanSummaryCompany.Success)
        assert not response.current_user_is_planner

    def test_that_correct_planner_id_is_shown(self):
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        response = self.get_plan_summary_company(plan.id, planner.id)
        assert_success(response, lambda s: s.planner_id == plan.planner.id)

    def test_that_correct_active_status_is_shown_when_plan_is_inactive(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(activation_date=None)
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.is_active == False)

    def test_that_correct_active_status_is_shown_when_plan_is_active(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.is_active == True)

    def test_that_correct_production_costs_are_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            )
        )
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(
            response,
            lambda s: all(
                [
                    s.means_cost == Decimal(1),
                    s.labour_cost == Decimal(2),
                    s.resources_cost == Decimal(3),
                ]
            ),
        )

    def test_that_correct_price_per_unit_is_shown_when_plan_is_public_service(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.price_per_unit == Decimal(0))

    def test_that_correct_price_per_unit_is_shown_when_plan_is_productive(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            is_public_service=False,
            amount=2,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.price_per_unit == Decimal(3))

    def test_that_correct_product_name_is_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(product_name="test product")
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.product_name == "test product")

    def test_that_correct_product_description_is_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(description="test description")
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.description == "test description")

    def test_that_correct_product_unit_is_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(production_unit="test unit")
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.production_unit == "test unit")

    def test_that_correct_amount_is_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(amount=123)
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.amount == 123)

    def test_that_correct_public_service_is_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_public_service=True)
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.is_public_service == True)

    def test_that_failure_is_returned_when_plan_does_not_exist(self):
        current_user = self.company_generator.create_company()
        self.assertIsInstance(
            self.get_plan_summary_company(uuid4(), current_user.id),
            GetPlanSummaryCompany.Failure,
        )

    def test_that_correct_availability_is_shown(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        assert plan.is_available
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.is_available == True)

    def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=None
        )
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.is_cooperating == False)
        assert_success(response, lambda s: s.cooperation is None)

    def test_that_correct_cooperation_is_shown(self):
        coop_generator = self.injector.get(CooperationGenerator)
        current_user = self.company_generator.create_company()
        coop = coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=coop
        )
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.is_cooperating == True)
        assert_success(response, lambda s: s.cooperation == coop.id)

    def test_that_zero_active_days_is_shown_if_plan_is_not_active_yet(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(activation_date=None)
        self.payout_use_case()
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.active_days == 0)

    def test_that_zero_active_days_is_shown_if_plan_is_active_since_less_than_one_day(
        self,
    ):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now()
        )
        self.payout_use_case()
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.active_days == 0)

    def test_that_one_active_days_is_shown_if_plan_is_active_since_25_hours(
        self,
    ):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_25_hours()
        )
        self.payout_use_case()
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.active_days == 1)

    def test_that_a_plans_timeframe_is_shown_as_active_days_if_plan_is_expired(
        self,
    ):
        current_user = self.company_generator.create_company()
        timeframe = 7
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_ten_days(),
            timeframe=timeframe,
        )
        self.payout_use_case()
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert_success(response, lambda s: s.active_days == timeframe)


def assert_success(
    response: Union[GetPlanSummaryCompany.Success, GetPlanSummaryCompany.Failure],
    assertion: Callable[[PlanSummary], bool],
) -> None:
    assert isinstance(response, GetPlanSummaryCompany.Success)
    assert isinstance(response.plan_summary, PlanSummary)
    assert assertion(response.plan_summary)
