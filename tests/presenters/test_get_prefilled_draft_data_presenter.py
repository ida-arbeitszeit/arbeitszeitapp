from decimal import Decimal
from uuid import uuid4

from arbeitszeit.use_cases import DraftSummarySuccess, PlanSummarySuccess
from arbeitszeit_web.get_prefilled_draft_data import GetPrefilledDraftDataPresenter

TEST_PLAN_SUMMARY_SUCCESS = PlanSummarySuccess(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
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
    get_prefilled_data = GetPrefilledDraftDataPresenter()
    result = get_prefilled_data.present(TEST_PLAN_SUMMARY_SUCCESS, True)
    assert result.from_expired_plan == True
    assert result.product_name == TEST_PLAN_SUMMARY_SUCCESS.product_name
    assert result.description == TEST_PLAN_SUMMARY_SUCCESS.description
    assert result.timeframe == str(TEST_PLAN_SUMMARY_SUCCESS.timeframe)
    assert result.production_unit == TEST_PLAN_SUMMARY_SUCCESS.production_unit
    assert result.amount == str(TEST_PLAN_SUMMARY_SUCCESS.amount)
    assert result.means_cost == str(TEST_PLAN_SUMMARY_SUCCESS.means_cost)
    assert result.resources_cost == str(TEST_PLAN_SUMMARY_SUCCESS.resources_cost)
    assert result.labour_cost == str(TEST_PLAN_SUMMARY_SUCCESS.labour_cost)
    assert result.is_public_service == TEST_PLAN_SUMMARY_SUCCESS.is_public_service


def test_correct_refilled_data_is_returned_for_draft_summary():
    get_prefilled_data = GetPrefilledDraftDataPresenter()
    result = get_prefilled_data.present(TEST_DRAFT_SUMMARY_SUCCESS, False)
    assert result.from_expired_plan == False
    assert result.product_name == TEST_DRAFT_SUMMARY_SUCCESS.product_name
    assert result.description == TEST_DRAFT_SUMMARY_SUCCESS.description
    assert result.timeframe == str(TEST_DRAFT_SUMMARY_SUCCESS.timeframe)
    assert result.production_unit == TEST_DRAFT_SUMMARY_SUCCESS.production_unit
    assert result.amount == str(TEST_DRAFT_SUMMARY_SUCCESS.amount)
    assert result.means_cost == str(TEST_DRAFT_SUMMARY_SUCCESS.means_cost)
    assert result.resources_cost == str(TEST_DRAFT_SUMMARY_SUCCESS.resources_cost)
    assert result.labour_cost == str(TEST_DRAFT_SUMMARY_SUCCESS.labour_cost)
    assert result.is_public_service == TEST_DRAFT_SUMMARY_SUCCESS.is_public_service
