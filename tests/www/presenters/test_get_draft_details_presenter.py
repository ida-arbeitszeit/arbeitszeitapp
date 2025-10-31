from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors.get_draft_details import DraftDetailsSuccess
from arbeitszeit_web.www.presenters.get_draft_details_presenter import (
    GetDraftDetailsPresenter,
)
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import PlanDetailsGenerator


class DraftDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetDraftDetailsPresenter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)

    def test_that_view_model_with_correct_cancel_url_is_returned(self) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(),
        )
        assert view_model.cancel_url == self.url_index.get_my_plans_url()

    @parameterized.expand(
        [
            ("product name",),
            ("  another product name  ",),
        ]
    )
    def test_that_product_name_is_returned_in_view_model(
        self, product_name: str
    ) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(product_name=product_name),
        )
        assert view_model.form.product_name_value == product_name

    @parameterized.expand(
        [
            ("description",),
            ("  another description  ",),
        ]
    )
    def test_that_description_is_returned_in_view_model(self, description: str) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(description=description),
        )
        assert view_model.form.description_value == description

    @parameterized.expand(
        [
            (15,),
            (20,),
        ]
    )
    def test_that_timeframe_is_returned_in_view_model(self, timeframe: int) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(timeframe=timeframe),
        )
        assert view_model.form.timeframe_value == str(timeframe)

    @parameterized.expand(
        [
            ("2 kilo",),
            ("  1 piece  ",),
        ]
    )
    def test_that_unit_of_distribution_is_returned_in_view_model(
        self, production_unit: str
    ) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(production_unit=production_unit),
        )
        assert view_model.form.unit_of_distribution_value == production_unit

    def test_that_amount_is_returned_in_view_model(
        self,
    ) -> None:
        expected_amount = 4
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(amount=expected_amount),
        )
        assert view_model.form.amount_value == str(expected_amount)

    @parameterized.expand(
        [
            (Decimal(0.1),),
            (Decimal(10),),
        ]
    )
    def test_that_means_cost_is_returned_in_view_model_rounded(
        self, means_cost: Decimal
    ) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(means_cost=means_cost),
        )
        assert view_model.form.means_cost_value == str(round(means_cost, 2))

    @parameterized.expand(
        [
            (Decimal(0.1),),
            (Decimal(10),),
        ]
    )
    def test_that_resources_cost_is_returned_in_view_model_rounded(
        self, resources_cost: Decimal
    ) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(resources_cost=resources_cost),
        )
        assert view_model.form.resource_cost_value == str(round(resources_cost, 2))

    @parameterized.expand(
        [
            (Decimal(0.1),),
            (Decimal(10),),
        ]
    )
    def test_that_labour_cost_is_returned_in_view_model_rounded(
        self, labour_cost: Decimal
    ) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(labour_cost=labour_cost),
        )
        assert view_model.form.labour_cost_value == str(round(labour_cost, 2))

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_is_public_service_is_returned_in_view_model(
        self, is_public_service: bool
    ) -> None:
        view_model = self.presenter.present_draft_details(
            self.create_draft_data(is_public_service=is_public_service),
        )
        assert view_model.form.is_public_plan_value == (
            "on" if is_public_service else ""
        )

    def create_draft_data(
        self,
        product_name: str = "test draft",
        description: str = "beschreibung draft",
        timeframe: int = 15,
        production_unit: str = "2 kilo",
        amount: int = 4,
        means_cost: Decimal = Decimal(7),
        resources_cost: Decimal = Decimal(7),
        labour_cost: Decimal = Decimal(7),
        is_public_service: bool = False,
        creation_timestamp: datetime = datetime_utc(2000, 1, 1),
    ) -> DraftDetailsSuccess:
        return DraftDetailsSuccess(
            planner_id=uuid4(),
            product_name=product_name,
            description=description,
            timeframe=timeframe,
            production_unit=production_unit,
            amount=amount,
            means_cost=means_cost,
            resources_cost=resources_cost,
            labour_cost=labour_cost,
            is_public_service=is_public_service,
            creation_timestamp=creation_timestamp,
        )
