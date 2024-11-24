from uuid import uuid4

from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.www.controllers.select_productive_consumption_controller import (
    SelectProductiveConsumptionController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class SelectProductiveConsumptionControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(SelectProductiveConsumptionController)

    def test_that_none_is_returned_when_no_plan_id_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.plan_id is None

    def test_that_input_error_is_raised_when_plan_id_is_not_a_valid_uuid(self) -> None:
        request = FakeRequest()
        request.set_arg("plan_id", "not_a_valid_uuid")
        with self.assertRaises(SelectProductiveConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)

    def test_that_a_warning_is_displayed_when_plan_id_is_not_a_valid_uuid(self) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("plan_id", "not_a_valid_uuid")
        with self.assertRaises(SelectProductiveConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_that_plan_id_from_url_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        plan_id = uuid4()
        request.set_arg("plan_id", str(plan_id))
        response = self.controller.process_input_data(request=request)
        assert response.plan_id == plan_id

    def test_that_plan_id_from_form_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        plan_id = uuid4()
        request.set_form("plan_id", str(plan_id))
        response = self.controller.process_input_data(request=request)
        assert response.plan_id == plan_id

    def test_that_none_is_returned_when_no_amount_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.amount is None

    def test_that_input_error_is_raised_when_amount_is_not_a_valid_number(self) -> None:
        request = FakeRequest()
        request.set_arg("amount", "not_a_valid_number")
        with self.assertRaises(SelectProductiveConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)

    def test_that_a_warning_is_displayed_when_amount_is_not_a_valid_number(
        self,
    ) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("amount", "not_a_valid_number")
        with self.assertRaises(SelectProductiveConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_that_amount_from_url_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        amount = 10
        request.set_arg("amount", str(amount))
        response = self.controller.process_input_data(request=request)
        assert response.amount == amount

    def test_that_amount_from_form_gets_passed_to_response_object(self) -> None:
        request = FakeRequest()
        amount = 10
        request.set_form("amount", str(amount))
        response = self.controller.process_input_data(request=request)
        assert response.amount == amount

    def test_that_none_is_returned_when_no_consumption_type_is_provided(self) -> None:
        request = FakeRequest()
        response = self.controller.process_input_data(request=request)
        assert response.consumption_type is None

    def test_that_input_error_is_raised_when_consumption_type_is_not_fixed_or_liquid(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg("type_of_consumption", "not_fixed_or_liquid")
        with self.assertRaises(SelectProductiveConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)

    def test_that_warning_is_displayed_when_consumption_type_is_not_fixed_or_liquid(
        self,
    ) -> None:
        request = FakeRequest()
        assert not self.notifier.warnings
        request.set_arg("type_of_consumption", "not_fixed_or_liquid")
        with self.assertRaises(SelectProductiveConsumptionController.InputDataError):
            self.controller.process_input_data(request=request)
        assert self.notifier.warnings

    def test_that_fixed_consumption_type_from_url_gets_passed_to_response_object(
        self,
    ) -> None:
        request = FakeRequest()
        expected_consumption_type = ConsumptionType.means_of_prod
        request.set_arg("type_of_consumption", "fixed")
        response = self.controller.process_input_data(request=request)
        assert response.consumption_type == expected_consumption_type

    def test_that_liquid_consumption_type_from_url_gets_passed_to_response_object(
        self,
    ) -> None:
        request = FakeRequest()
        expected_consumption_type = ConsumptionType.raw_materials
        request.set_arg("type_of_consumption", "liquid")
        response = self.controller.process_input_data(request=request)
        assert response.consumption_type == expected_consumption_type

    def test_that_fixed_consumption_type_from_form_gets_passed_to_response_object(
        self,
    ) -> None:
        request = FakeRequest()
        expected_consumption_type = ConsumptionType.means_of_prod
        request.set_form("type_of_consumption", "fixed")
        response = self.controller.process_input_data(request=request)
        assert response.consumption_type == expected_consumption_type

    def test_that_liquid_consumption_type_from_form_gets_passed_to_response_object(
        self,
    ) -> None:
        request = FakeRequest()
        expected_consumption_type = ConsumptionType.raw_materials
        request.set_form("type_of_consumption", "liquid")
        response = self.controller.process_input_data(request=request)
        assert response.consumption_type == expected_consumption_type
