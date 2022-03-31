from dataclasses import replace
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import CreatePlanDraft, CreatePlanDraftRequest
from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraftResponse
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test
from .repositories import PlanDraftRepository

REQUEST = CreatePlanDraftRequest(
    planner=uuid4(),
    costs=ProductionCosts(
        Decimal(1),
        Decimal(1),
        Decimal(1),
    ),
    product_name="testproduct",
    production_unit="kg",
    production_amount=10,
    description="test description",
    is_public_service=False,
    timeframe_in_days=7,
)


@injection_test
def test_that_create_plan_creates_a_plan_draft_that_is_not_rejected(
    plan_draft_repository: PlanDraftRepository,
    create_plan_draft: CreatePlanDraft,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    request = replace(REQUEST, planner=planner.id)
    assert not len(plan_draft_repository)
    response = create_plan_draft(request)
    assert len(plan_draft_repository) == 1
    assert not response.is_rejected


@injection_test
def test_that_create_plan_returns_a_draft_id(
    create_plan_draft: CreatePlanDraft,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    request = replace(REQUEST, planner=planner.id)
    response = create_plan_draft(request)
    assert response.draft_id


@injection_test
def test_that_create_plan_gets_rejected_with_non_existing_planner(
    create_plan_draft: CreatePlanDraft,
):
    request = replace(
        REQUEST,
        planner=uuid4(),
    )
    response = create_plan_draft(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == CreatePlanDraftResponse.RejectionReason.planner_does_not_exist
    )
    assert not response.draft_id


@injection_test
def test_that_create_plan_gets_rejected_with_negative_production_costs(
    create_plan_draft: CreatePlanDraft,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    request = replace(
        REQUEST,
        planner=planner.id,
        costs=ProductionCosts(Decimal(-1), Decimal(-1), Decimal(-1)),
    )
    response = create_plan_draft(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == CreatePlanDraftResponse.RejectionReason.negative_plan_input
    )
    assert not response.draft_id


@injection_test
def test_that_create_plan_gets_rejected_with_negative_production_amount(
    create_plan_draft: CreatePlanDraft,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    request = replace(
        REQUEST,
        planner=planner.id,
        production_amount=-1,
    )
    response = create_plan_draft(request)
    assert response.is_rejected
    assert not response.draft_id


@injection_test
def test_that_create_plan_gets_rejected_with_negative_timeframe(
    create_plan_draft: CreatePlanDraft,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    request = replace(
        REQUEST,
        planner=planner.id,
        timeframe_in_days=-1,
    )
    response = create_plan_draft(request)
    assert response.is_rejected
    assert not response.draft_id


@injection_test
def test_that_drafted_plan_has_same_planner_as_specified_on_creation(
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    planner = company_generator.create_company()
    draft = plan_generator.draft_plan(planner=planner)
    assert draft.planner.id == planner.id
