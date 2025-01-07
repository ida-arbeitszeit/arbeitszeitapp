from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.use_cases.get_draft_details import DraftDetailsSuccess
from arbeitszeit_web.www.presenters.get_draft_details_presenter import (
    GetDraftDetailsPresenter,
)
from tests.forms import DraftForm
from tests.www.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import PlanDetailsGenerator

TEST_DRAFT_SUMMARY_SUCCESS = DraftDetailsSuccess(
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
    creation_timestamp=datetime(2000, 1, 1),
)


class PlanDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetDraftDetailsPresenter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)
        self.plan_details = self.plan_details_generator.create_plan_details()

    def test_correct_form_data_is_returned_for_plan_details(self) -> None:
        form = DraftForm()
        self.presenter.present_draft_details(self.plan_details, form=form)
        assert form.product_name_field().get_value() == self.plan_details.product_name
        assert form.description_field().get_value() == self.plan_details.description
        assert form.timeframe_field().get_value() == self.plan_details.timeframe
        assert (
            form.unit_of_distribution_field().get_value()
            == self.plan_details.production_unit
        )
        assert form.amount_field().get_value() == self.plan_details.amount
        assert form.means_cost_field().get_value() == self.plan_details.means_cost
        assert (
            form.resource_cost_field().get_value() == self.plan_details.resources_cost
        )
        assert form.labour_cost_field().get_value() == self.plan_details.labour_cost
        assert (
            form.is_public_service_field().get_value()
            == self.plan_details.is_public_service
        )

    def test_correct_view_model_is_returned_for_plan_details(self) -> None:
        form = DraftForm()
        view_model = self.presenter.present_draft_details(self.plan_details, form=form)
        self.assertEqual(view_model.cancel_url, self.url_index.get_my_plans_url())


class DraftDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetDraftDetailsPresenter)

    def test_correct_form_data_is_returned_for_draft_details(self) -> None:
        form = DraftForm()
        self.presenter.present_draft_details(
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

    def test_correct_view_model_is_returned_for_draft_details(self) -> None:
        form = DraftForm()
        view_model = self.presenter.present_draft_details(
            TEST_DRAFT_SUMMARY_SUCCESS, form=form
        )
        self.assertEqual(view_model.cancel_url, self.url_index.get_my_plans_url())
