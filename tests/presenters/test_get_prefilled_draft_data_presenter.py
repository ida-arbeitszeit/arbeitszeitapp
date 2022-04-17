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


def test_correct_refilled_data_is_returned_for_plan_summary():
    injector = get_dependency_injector()
    get_prefilled_data = injector.get(GetPrefilledDraftDataPresenter)
    result = get_prefilled_data.present(BUSINESS_PLAN_SUMMARY)
    assert result.product_name == BUSINESS_PLAN_SUMMARY.product_name
    assert result.description == BUSINESS_PLAN_SUMMARY.description
    assert result.timeframe == str(BUSINESS_PLAN_SUMMARY.timeframe)
    assert result.production_unit == BUSINESS_PLAN_SUMMARY.production_unit
    assert result.amount == str(BUSINESS_PLAN_SUMMARY.amount)
    assert result.means_cost == str(BUSINESS_PLAN_SUMMARY.means_cost)
    assert result.resources_cost == str(BUSINESS_PLAN_SUMMARY.resources_cost)
    assert result.labour_cost == str(BUSINESS_PLAN_SUMMARY.labour_cost)
    assert result.is_public_service == BUSINESS_PLAN_SUMMARY.is_public_service


def test_correct_refilled_data_is_returned_for_draft_summary():
    injector = get_dependency_injector()
    get_prefilled_data = injector.get(GetPrefilledDraftDataPresenter)
    result = get_prefilled_data.present(TEST_DRAFT_SUMMARY_SUCCESS)
    assert result.product_name == TEST_DRAFT_SUMMARY_SUCCESS.product_name
    assert result.description == TEST_DRAFT_SUMMARY_SUCCESS.description
    assert result.timeframe == str(TEST_DRAFT_SUMMARY_SUCCESS.timeframe)
    assert result.production_unit == TEST_DRAFT_SUMMARY_SUCCESS.production_unit
    assert result.amount == str(TEST_DRAFT_SUMMARY_SUCCESS.amount)
    assert result.means_cost == str(TEST_DRAFT_SUMMARY_SUCCESS.means_cost)
    assert result.resources_cost == str(TEST_DRAFT_SUMMARY_SUCCESS.resources_cost)
    assert result.labour_cost == str(TEST_DRAFT_SUMMARY_SUCCESS.labour_cost)
    assert result.is_public_service == TEST_DRAFT_SUMMARY_SUCCESS.is_public_service
