from decimal import Decimal
from uuid import uuid4

from arbeitszeit.use_cases.get_draft_summary import DraftSummarySuccess
from arbeitszeit_web.www.presenters.create_draft_presenter import (
    GetPrefilledDraftDataPresenter,
)
from tests.forms import DraftForm
from tests.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import PlanSummaryGenerator
from tests.presenters.url_index import UrlIndexTestImpl

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


class PlanSummaryPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPrefilledDraftDataPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.plan_summary_generator = self.injector.get(PlanSummaryGenerator)
        self.plan_summary = self.plan_summary_generator.create_plan_summary()

    def test_correct_form_data_is_returned_for_plan_summary(self) -> None:
        form = DraftForm()
        self.presenter.show_prefilled_draft_data(self.plan_summary, form=form)
        assert form.product_name_field().get_value() == self.plan_summary.product_name
        assert form.description_field().get_value() == self.plan_summary.description
        assert form.timeframe_field().get_value() == self.plan_summary.timeframe
        assert (
            form.unit_of_distribution_field().get_value()
            == self.plan_summary.production_unit
        )
        assert form.amount_field().get_value() == self.plan_summary.amount
        assert form.means_cost_field().get_value() == self.plan_summary.means_cost
        assert (
            form.resource_cost_field().get_value() == self.plan_summary.resources_cost
        )
        assert form.labour_cost_field().get_value() == self.plan_summary.labour_cost
        assert (
            form.is_public_service_field().get_value()
            == self.plan_summary.is_public_service
        )

    def test_correct_view_model_is_returned_for_plan_summary(self) -> None:
        form = DraftForm()
        view_model = self.presenter.show_prefilled_draft_data(
            self.plan_summary, form=form
        )
        self.assertEqual(view_model.cancel_url, self.url_index.get_create_draft_url())
        self.assertEqual(
            view_model.save_draft_url, self.url_index.get_create_draft_url()
        )
        self.assertEqual(
            view_model.load_draft_url, self.url_index.get_my_plan_drafts_url()
        )


class DraftSummaryPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPrefilledDraftDataPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_correct_form_data_is_returned_for_draft_summary(self) -> None:
        form = DraftForm()
        self.presenter.show_prefilled_draft_data(
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

    def test_correct_view_model_is_returned_for_draft_summary(self) -> None:
        form = DraftForm()
        view_model = self.presenter.show_prefilled_draft_data(
            TEST_DRAFT_SUMMARY_SUCCESS, form=form
        )
        self.assertEqual(view_model.cancel_url, self.url_index.get_create_draft_url())
        self.assertEqual(
            view_model.save_draft_url, self.url_index.get_create_draft_url()
        )
        self.assertEqual(
            view_model.load_draft_url, self.url_index.get_my_plan_drafts_url()
        )
