from datetime import datetime
from decimal import Decimal
from typing import Callable
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases import (
    GetPlanSummaryCompany,
    PlanSummaryCompanyResponse,
    PlanSummaryCompanySuccess,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


class Tests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.get_plan_summary_company = self.injector.get(GetPlanSummaryCompany)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_current_user_is_correctly_shown_as_planner(self):
        planner_and_current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner_and_current_user)
        response = self.get_plan_summary_company(plan.id, planner_and_current_user.id)
        assert isinstance(response, PlanSummaryCompanySuccess)
        assert response.current_user_is_planner

    def test_that_current_user_is_correctly_shown_as_non_planner(self):
        current_user = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        response = self.get_plan_summary_company(plan.id, current_user.id)
        assert isinstance(response, PlanSummaryCompanySuccess)
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

    def test_that_none_is_returned_when_plan_does_not_exist(self) -> None:
        current_user = self.company_generator.create_company()
        assert self.get_plan_summary_company(uuid4(), current_user.id) is None

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


def assert_success(
    response: PlanSummaryCompanyResponse,
    assertion: Callable[[BusinessPlanSummary], bool],
) -> None:
    assert isinstance(response, PlanSummaryCompanySuccess)
    assert isinstance(response.plan_summary, BusinessPlanSummary)
    assert assertion(response.plan_summary)
