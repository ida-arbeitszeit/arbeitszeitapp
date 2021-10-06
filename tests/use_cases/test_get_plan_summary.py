from datetime import datetime
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import (
    GetPlanSummary,
    PlanSummaryResponse,
    PlanSummarySuccess,
)
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_correct_planner_id_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    plan = plan_generator.create_plan(planner=planner)
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.planner_id == plan.planner.id)


@injection_test
def test_that_correct_active_status_is_shown_when_plan_is_inactive(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(activation_date=None)
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.is_active == False)


@injection_test
def test_that_correct_active_status_is_shown_when_plan_is_active(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.is_active == True)


@injection_test
def test_that_correct_production_costs_are_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        )
    )
    summary = get_plan_summary(plan.id)
    assert_success(
        summary,
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
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(
        is_public_service=True,
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        ),
    )
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.price_per_unit == Decimal(0))


@injection_test
def test_that_correct_price_per_unit_is_shown_when_plan_is_productive(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(
        is_public_service=False,
        amount=2,
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        ),
    )
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.price_per_unit == Decimal(3))


@injection_test
def test_that_correct_product_name_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(product_name="test product")
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.product_name == "test product")


@injection_test
def test_that_correct_product_description_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(description="test description")
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.description == "test description")


@injection_test
def test_that_correct_product_unit_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(production_unit="test unit")
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.production_unit == "test unit")


@injection_test
def test_that_correct_amount_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(amount=123)
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.amount == 123)


@injection_test
def test_that_correct_public_service_is_shown(
    plan_generator: PlanGenerator,
    get_plan_summary: GetPlanSummary,
):
    plan = plan_generator.create_plan(is_public_service=True)
    summary = get_plan_summary(plan.id)
    assert_success(summary, lambda s: s.is_public_service == True)


@injection_test
def test_that_none_is_returned_when_plan_does_not_exist(
    get_plan_summary: GetPlanSummary,
) -> None:
    assert get_plan_summary(uuid4()) is None


def assert_success(
    response: PlanSummaryResponse, assertion: Callable[[PlanSummarySuccess], bool]
) -> None:
    assert isinstance(response, PlanSummarySuccess)
    assert assertion(response)
