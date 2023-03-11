from decimal import Decimal
from typing import Callable
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases.get_draft_summary import (
    DraftSummaryResponse,
    DraftSummarySuccess,
    GetDraftSummary,
)
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_correct_planner_id_is_returned(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    draft = plan_generator.draft_plan(planner=planner)
    summary = get_draft_summary(draft.id)
    assert_success(summary, lambda s: s.planner_id == planner)


@injection_test
def test_that_correct_production_costs_are_shown(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
):
    draft = plan_generator.draft_plan(
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        )
    )
    summary = get_draft_summary(draft.id)
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
def test_that_correct_product_name_is_shown(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
):
    draft = plan_generator.draft_plan(product_name="test product")
    summary = get_draft_summary(draft.id)
    assert_success(summary, lambda s: s.product_name == "test product")


@injection_test
def test_that_correct_product_description_is_shown(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
):
    draft = plan_generator.draft_plan(description="test description")
    summary = get_draft_summary(draft.id)
    assert_success(summary, lambda s: s.description == "test description")


@injection_test
def test_that_correct_product_unit_is_shown(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
):
    draft = plan_generator.draft_plan(production_unit="test unit")
    summary = get_draft_summary(draft.id)
    assert_success(summary, lambda s: s.production_unit == "test unit")


@injection_test
def test_that_correct_amount_is_shown(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
):
    draft = plan_generator.draft_plan(amount=123)
    summary = get_draft_summary(draft.id)
    assert_success(summary, lambda s: s.amount == 123)


@injection_test
def test_that_correct_public_service_is_shown(
    plan_generator: PlanGenerator,
    get_draft_summary: GetDraftSummary,
):
    draft = plan_generator.draft_plan(is_public_service=True)
    summary = get_draft_summary(draft.id)
    assert_success(summary, lambda s: s.is_public_service == True)


@injection_test
def test_that_none_is_returned_when_draft_does_not_exist(
    get_draft_summary: GetDraftSummary,
) -> None:
    assert get_draft_summary(uuid4()) is None


def assert_success(
    response: DraftSummaryResponse, assertion: Callable[[DraftSummarySuccess], bool]
) -> None:
    assert isinstance(response, DraftSummarySuccess)
    assert assertion(response)
