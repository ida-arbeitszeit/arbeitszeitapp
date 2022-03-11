from datetime import datetime
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases import (
    GetPlanSummaryCompany,
    PlanSummaryCompanyResponse,
    PlanSummaryCompanySuccess,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_current_user_is_correctly_shown_as_planner(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    planner_and_current_user = company_generator.create_company()
    plan = plan_generator.create_plan(planner=planner_and_current_user)
    response = get_plan_summary_company(plan.id, planner_and_current_user.id)
    assert isinstance(response, PlanSummaryCompanySuccess)
    assert response.current_user_is_planner


@injection_test
def test_that_current_user_is_correctly_shown_as_non_planner(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan()
    response = get_plan_summary_company(plan.id, current_user.id)
    assert isinstance(response, PlanSummaryCompanySuccess)
    assert not response.current_user_is_planner


@injection_test
def test_that_correct_planner_id_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    plan = plan_generator.create_plan(planner=planner)
    response = get_plan_summary_company(plan.id, planner.id)
    assert_success(response, lambda s: s.planner_id == plan.planner.id)


@injection_test
def test_that_correct_active_status_is_shown_when_plan_is_inactive(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=None)
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.is_active == False)


@injection_test
def test_that_correct_active_status_is_shown_when_plan_is_active(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.min)
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.is_active == True)


@injection_test
def test_that_correct_production_costs_are_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        )
    )
    response = get_plan_summary_company(plan.id, current_user.id)
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


@injection_test
def test_that_correct_price_per_unit_is_shown_when_plan_is_public_service(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(
        is_public_service=True,
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        ),
    )
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.price_per_unit == Decimal(0))


@injection_test
def test_that_correct_price_per_unit_is_shown_when_plan_is_productive(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(
        is_public_service=False,
        amount=2,
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        ),
    )
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.price_per_unit == Decimal(3))


@injection_test
def test_that_correct_product_name_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(product_name="test product")
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.product_name == "test product")


@injection_test
def test_that_correct_product_description_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(description="test description")
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.description == "test description")


@injection_test
def test_that_correct_product_unit_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(production_unit="test unit")
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.production_unit == "test unit")


@injection_test
def test_that_correct_amount_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(amount=123)
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.amount == 123)


@injection_test
def test_that_correct_public_service_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(is_public_service=True)
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.is_public_service == True)


@injection_test
def test_that_none_is_returned_when_plan_does_not_exist(
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
) -> None:
    current_user = company_generator.create_company()
    assert get_plan_summary_company(uuid4(), current_user.id) is None


@injection_test
def test_that_correct_availability_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan()
    assert plan.is_available
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.is_available == True)


@injection_test
def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.min, cooperation=None)
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.is_cooperating == False)
    assert_success(response, lambda s: s.cooperation is None)


@injection_test
def test_that_correct_cooperation_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary_company: GetPlanSummaryCompany,
    coop_generator: CooperationGenerator,
    company_generator: CompanyGenerator,
):
    current_user = company_generator.create_company()
    coop = coop_generator.create_cooperation()
    plan = plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    response = get_plan_summary_company(plan.id, current_user.id)
    assert_success(response, lambda s: s.is_cooperating == True)
    assert_success(response, lambda s: s.cooperation == coop.id)


def assert_success(
    response: PlanSummaryCompanyResponse,
    assertion: Callable[[BusinessPlanSummary], bool],
) -> None:
    assert isinstance(response, PlanSummaryCompanySuccess)
    assert isinstance(response.plan_summary, BusinessPlanSummary)
    assert assertion(response.plan_summary)
