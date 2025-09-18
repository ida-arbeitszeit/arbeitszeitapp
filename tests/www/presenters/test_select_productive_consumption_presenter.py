from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.interactors import select_productive_consumption
from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.www.presenters.select_productive_consumption_presenter import (
    SelectProductiveConsumptionPresenter,
)
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(SelectProductiveConsumptionPresenter)

    @parameterized.expand(
        [
            (None, None),
            (5, ConsumptionType.means_of_prod),
            (10, ConsumptionType.raw_materials),
        ]
    )
    def test_that_no_plan_response_gets_rendered_correctly(
        self,
        amount: int | None,
        consumption_type: ConsumptionType | None,
    ):
        response = self.create_no_plan_response(amount, consumption_type)
        view_model = self.presenter.render_response(response)
        assert view_model.valid_plan_selected is False
        assert view_model.plan_id is None
        assert view_model.plan_name is None
        assert view_model.plan_description is None
        assert view_model.amount == amount
        assert view_model.is_consumption_of_fixed_means == (
            consumption_type == ConsumptionType.means_of_prod
        )
        assert view_model.status_code == 200

    def test_that_warning_is_displayed_when_plan_is_invalid(self):
        assert not self.notifier.warnings
        response = self.create_invalid_plan_response(5, ConsumptionType.means_of_prod)
        self.presenter.render_response(response)
        assert self.notifier.warnings

    @parameterized.expand(
        [
            (None, None),
            (5, ConsumptionType.means_of_prod),
            (10, ConsumptionType.raw_materials),
        ]
    )
    def test_that_invalid_plan_response_gets_rendered_correctly(
        self,
        amount: int | None,
        consumption_type: ConsumptionType | None,
    ):
        response = self.create_invalid_plan_response(amount, consumption_type)
        view_model = self.presenter.render_response(response)
        assert view_model.valid_plan_selected is False
        assert view_model.plan_id is None
        assert view_model.plan_name is None
        assert view_model.plan_description is None
        assert view_model.amount == amount
        assert view_model.is_consumption_of_fixed_means == (
            consumption_type == ConsumptionType.means_of_prod
        )
        assert view_model.status_code == 404

    @parameterized.expand(
        [
            (
                uuid4(),
                5,
                ConsumptionType.means_of_prod,
                "Plan Name",
                "Plan Description",
            ),
            (
                uuid4(),
                10,
                ConsumptionType.raw_materials,
                "Plan Name",
                "Plan Description",
            ),
            (
                uuid4(),
                None,
                ConsumptionType.means_of_prod,
                "Plan Name",
                "Plan Description",
            ),
            (uuid4(), 5, None, "Plan Name", "Plan Description"),
        ]
    )
    def test_that_valid_plan_response_gets_rendered_correctly(
        self,
        plan_id: UUID,
        amount: int | None,
        consumption_type: ConsumptionType | None,
        plan_name: str,
        plan_description: str,
    ):
        response = self.create_valid_plan_response(
            plan_id, amount, consumption_type, plan_name, plan_description
        )
        view_model = self.presenter.render_response(response)
        assert view_model.valid_plan_selected is True
        assert view_model.plan_id == str(plan_id)
        assert view_model.plan_name == plan_name
        assert view_model.plan_description == plan_description
        assert view_model.amount == amount
        assert view_model.is_consumption_of_fixed_means == (
            consumption_type == ConsumptionType.means_of_prod
        )
        assert view_model.status_code == 200

    def create_no_plan_response(
        self,
        amount: int | None,
        consumption_type: ConsumptionType | None,
    ) -> select_productive_consumption.NoPlanResponse:
        return select_productive_consumption.NoPlanResponse(amount, consumption_type)

    def create_invalid_plan_response(
        self,
        amount: int | None,
        consumption_type: ConsumptionType | None,
    ) -> select_productive_consumption.InvalidPlanResponse:
        return select_productive_consumption.InvalidPlanResponse(
            amount, consumption_type
        )

    def create_valid_plan_response(
        self,
        plan_id: UUID,
        amount: int | None,
        consumption_type: ConsumptionType | None,
        plan_name: str,
        plan_description: str,
    ) -> select_productive_consumption.ValidPlanResponse:
        return select_productive_consumption.ValidPlanResponse(
            plan_id,
            amount,
            consumption_type,
            plan_name,
            plan_description,
        )
