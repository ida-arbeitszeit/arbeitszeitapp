from arbeitszeit.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionResponse as InteractorResponse,
)
from arbeitszeit_web.api.presenters.interfaces import JsonBoolean, JsonObject
from arbeitszeit_web.api.presenters.liquid_means_consumption_presenter import (
    LiquidMeansConsumptionPresenter,
)
from arbeitszeit_web.api.response_errors import Forbidden, NotFound
from tests.api.presenters.base_test_case import BaseTestCase


class TestViewModelCreation(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(LiquidMeansConsumptionPresenter)

    def test_view_model_returns_success_is_true_if_interactor_was_successful(
        self,
    ) -> None:
        response = InteractorResponse(rejection_reason=None)
        view_model = self.presenter.create_view_model(response)
        assert view_model.success

    def test_view_model_raises_not_found_if_plan_was_not_found(self) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.plan_not_found
        )
        with self.assertRaises(NotFound):
            self.presenter.create_view_model(response)

    def test_view_model_shows_error_message_if_plan_was_not_found(self) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.plan_not_found
        )
        with self.assertRaises(NotFound) as err:
            self.presenter.create_view_model(response)
        assert err.exception.message == "Plan does not exist."

    def test_view_model_raises_not_found_if_plan_has_expired(self) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.plan_is_not_active
        )
        with self.assertRaises(NotFound):
            self.presenter.create_view_model(response)

    def test_view_model_shows_error_message_if_plan_has_expired(self) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.plan_is_not_active
        )
        with self.assertRaises(NotFound) as err:
            self.presenter.create_view_model(response)
        assert err.exception.message == "The specified plan has expired."

    def test_view_model_raises_forbidden_if_company_tries_to_acquire_public_product(
        self,
    ) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.cannot_consume_public_service
        )
        with self.assertRaises(Forbidden):
            self.presenter.create_view_model(response)

    def test_view_model_shows_error_message_if_company_tries_to_acquire_public_product(
        self,
    ) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.cannot_consume_public_service
        )
        with self.assertRaises(Forbidden) as err:
            self.presenter.create_view_model(response)
        assert err.exception.message == "Companies cannot acquire public products."

    def test_view_model_raises_forbidden_if_company_tries_to_acquire_its_own_product(
        self,
    ) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.consumer_is_planner
        )
        with self.assertRaises(Forbidden):
            self.presenter.create_view_model(response)

    def test_view_model_shows_error_message_if_company_tries_to_acquire_its_own_product(
        self,
    ) -> None:
        response = InteractorResponse(
            rejection_reason=InteractorResponse.RejectionReason.consumer_is_planner
        )
        with self.assertRaises(Forbidden) as err:
            self.presenter.create_view_model(response)
        assert err.exception.message == "Companies cannot acquire their own products."


class TestSchema(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(LiquidMeansConsumptionPresenter)
        self.schema = self.presenter.get_schema()

    def test_schema_is_of_type_object(self) -> None:
        assert isinstance(self.schema, JsonObject)

    def test_schema_is_required(self) -> None:
        assert self.schema.required

    def test_schema_name_is_as_expected(self) -> None:
        assert isinstance(self.schema, JsonObject)
        assert self.schema.name == "LiquidMeansConsumptionResponse"

    def test_schema_has_one_top_level_member(self) -> None:
        assert isinstance(self.schema, JsonObject)
        assert len(self.schema.members) == 1

    def test_member_has_name_success(self) -> None:
        assert isinstance(self.schema, JsonObject)
        assert "success" in self.schema.members

    def test_member_is_of_type_boolean(self) -> None:
        assert isinstance(self.schema, JsonObject)
        assert isinstance(self.schema.members["success"], JsonBoolean)

    def test_member_success_is_required(self) -> None:
        assert isinstance(self.schema, JsonObject)
        assert self.schema.members["success"].required
