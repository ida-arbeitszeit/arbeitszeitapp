from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases import DraftSummarySuccess
from arbeitszeit_web.create_draft import GetPrefilledDraftDataPresenter
from tests.presenters.forms import DraftForm

from .dependency_injection import get_dependency_injector

PLAN_SUMMARY = PlanSummary(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
    planner_name="test name",
    product_name="test",
    description="beschreibung",
    timeframe=10,
    active_days=5,
    production_unit="1 kilo",
    amount=2,
    means_cost=Decimal(5),
    resources_cost=Decimal(5),
    labour_cost=Decimal(5),
    is_public_service=True,
    price_per_unit=Decimal(10),
    is_available=True,
    is_cooperating=False,
    cooperation=None,
    creation_date=datetime.now(),
    approval_date=None,
    expiration_date=None,
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


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.get_prefilled_data = self.injector.get(GetPrefilledDraftDataPresenter)

    def test_correct_prefilled_data_is_returned_for_plan_summary(self) -> None:
        form = DraftForm()
        self.get_prefilled_data.show_prefilled_draft_data(PLAN_SUMMARY, form=form)
        assert form.product_name_field().get_value() == PLAN_SUMMARY.product_name
        assert form.description_field().get_value() == PLAN_SUMMARY.description
        assert form.timeframe_field().get_value() == PLAN_SUMMARY.timeframe
        assert (
            form.unit_of_distribution_field().get_value()
            == PLAN_SUMMARY.production_unit
        )
        assert form.amount_field().get_value() == PLAN_SUMMARY.amount
        assert form.means_cost_field().get_value() == PLAN_SUMMARY.means_cost
        assert form.resource_cost_field().get_value() == PLAN_SUMMARY.resources_cost
        assert form.labour_cost_field().get_value() == PLAN_SUMMARY.labour_cost
        assert (
            form.is_public_service_field().get_value() == PLAN_SUMMARY.is_public_service
        )

    def test_correct_prefilled_data_is_returned_for_draft_summary(self) -> None:
        form = DraftForm()
        self.get_prefilled_data.show_prefilled_draft_data(
            TEST_DRAFT_SUMMARY_SUCCESS,
            form=form,
        )
        assert (
            form.product_name_field().get_value()
            == TEST_DRAFT_SUMMARY_SUCCESS.product_name
        )
        assert (
            form.description_field().get_value()
            == TEST_DRAFT_SUMMARY_SUCCESS.description
        )
        assert (
            form.timeframe_field().get_value() == TEST_DRAFT_SUMMARY_SUCCESS.timeframe
        )
        assert (
            form.unit_of_distribution_field().get_value()
            == TEST_DRAFT_SUMMARY_SUCCESS.production_unit
        )
        assert form.amount_field().get_value() == TEST_DRAFT_SUMMARY_SUCCESS.amount
        assert (
            form.means_cost_field().get_value() == TEST_DRAFT_SUMMARY_SUCCESS.means_cost
        )
        assert (
            form.resource_cost_field().get_value()
            == TEST_DRAFT_SUMMARY_SUCCESS.resources_cost
        )
        assert (
            form.labour_cost_field().get_value()
            == TEST_DRAFT_SUMMARY_SUCCESS.labour_cost
        )
        assert (
            form.is_public_service_field().get_value()
            == TEST_DRAFT_SUMMARY_SUCCESS.is_public_service
        )
