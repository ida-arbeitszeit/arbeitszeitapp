from decimal import Decimal
from uuid import uuid4

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases import DraftSummarySuccess
from arbeitszeit_web.get_prefilled_draft_data import GetPrefilledDraftDataPresenter

from .dependency_injection import get_dependency_injector

BUSINESS_PLAN_SUMMARY = BusinessPlanSummary(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
    planner_name="test name",
    product_name="test",
    description="beschreibung",
    timeframe=10,
    production_unit="1 kilo",
    amount=2,
    means_cost=Decimal(5),
    resources_cost=Decimal(5),
    labour_cost=Decimal(5),
    is_public_service=False,
    price_per_unit=Decimal(10),
    is_available=True,
    is_cooperating=False,
    cooperation=None,
)

TEST_DRAFT_SUMMARY_SUCCESS = DraftSummarySuccess(
    draft_id=uuid4(),
    planner_id=uuid4(),
    product_name="test draft",
    description="beschreibung draft",
    timeframe=15,
    production_unit="2 kilo",
    amount=4,
    means_cost=Decimal(7),
    resources_cost=Decimal(7),
    labour_cost=Decimal(7),
    is_public_service=False,
)


def test_correct_prefilled_data_is_returned_for_plan_summary():
    injector = get_dependency_injector()
    get_prefilled_data = injector.get(GetPrefilledDraftDataPresenter)
    view_model = get_prefilled_data.show_prefilled_draft_data(BUSINESS_PLAN_SUMMARY)
    assert (
        view_model.prefilled_draft_data.prd_name == BUSINESS_PLAN_SUMMARY.product_name
    )
    assert (
        view_model.prefilled_draft_data.description == BUSINESS_PLAN_SUMMARY.description
    )
    assert view_model.prefilled_draft_data.timeframe == BUSINESS_PLAN_SUMMARY.timeframe
    assert (
        view_model.prefilled_draft_data.prd_unit
        == BUSINESS_PLAN_SUMMARY.production_unit
    )
    assert view_model.prefilled_draft_data.prd_amount == BUSINESS_PLAN_SUMMARY.amount
    assert view_model.prefilled_draft_data.costs_p == BUSINESS_PLAN_SUMMARY.means_cost
    assert (
        view_model.prefilled_draft_data.costs_r == BUSINESS_PLAN_SUMMARY.resources_cost
    )
    assert view_model.prefilled_draft_data.costs_a == BUSINESS_PLAN_SUMMARY.labour_cost
    assert (
        view_model.prefilled_draft_data.productive_or_public == "public"
        if BUSINESS_PLAN_SUMMARY.is_public_service
        else "productive"
    )
    assert view_model.prefilled_draft_data.action == ""


def test_correct_prefilled_data_is_returned_for_draft_summary():
    injector = get_dependency_injector()
    get_prefilled_data = injector.get(GetPrefilledDraftDataPresenter)
    view_model = get_prefilled_data.show_prefilled_draft_data(
        TEST_DRAFT_SUMMARY_SUCCESS
    )
    assert (
        view_model.prefilled_draft_data.prd_name
        == TEST_DRAFT_SUMMARY_SUCCESS.product_name
    )
    assert (
        view_model.prefilled_draft_data.description
        == TEST_DRAFT_SUMMARY_SUCCESS.description
    )
    assert (
        view_model.prefilled_draft_data.timeframe
        == TEST_DRAFT_SUMMARY_SUCCESS.timeframe
    )
    assert (
        view_model.prefilled_draft_data.prd_unit
        == TEST_DRAFT_SUMMARY_SUCCESS.production_unit
    )
    assert (
        view_model.prefilled_draft_data.prd_amount == TEST_DRAFT_SUMMARY_SUCCESS.amount
    )
    assert (
        view_model.prefilled_draft_data.costs_p == TEST_DRAFT_SUMMARY_SUCCESS.means_cost
    )
    assert (
        view_model.prefilled_draft_data.costs_r
        == TEST_DRAFT_SUMMARY_SUCCESS.resources_cost
    )
    assert (
        view_model.prefilled_draft_data.costs_a
        == TEST_DRAFT_SUMMARY_SUCCESS.labour_cost
    )
    assert (
        view_model.prefilled_draft_data.productive_or_public == "public"
        if TEST_DRAFT_SUMMARY_SUCCESS.is_public_service
        else "productive"
    )
    assert view_model.prefilled_draft_data.action == ""
