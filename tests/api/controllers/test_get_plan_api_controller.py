from uuid import uuid4

from arbeitszeit_web.api.controllers.get_plan_api_controller import (
    GetPlanApiController,
    plan_detail_expected_input,
)
from arbeitszeit_web.api.controllers.parameters import PathParameter
from arbeitszeit_web.api.response_errors import BadRequest
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(GetPlanApiController)

    def test_plan_id_string_in_uuid_format_gets_converted_to_use_case_request(
        self,
    ) -> None:
        expected_plan_id = uuid4()
        plan_id = str(expected_plan_id)
        self.controller.create_request(plan_id)

    def test_plan_id_string_in_uuid_format_gets_converted_to_use_case_request_with_correct_plan_id(
        self,
    ) -> None:
        expected_plan_id = uuid4()
        plan_id = str(expected_plan_id)
        use_case_request = self.controller.create_request(plan_id)
        self.assertEqual(use_case_request.plan_id, expected_plan_id)

    def test_plan_id_string_in_uuid_format_with_whitespace_gets_converted_to_uuid(
        self,
    ) -> None:
        expected_plan_id = uuid4()
        plan_id = f"  {expected_plan_id}  "
        use_case_request = self.controller.create_request(plan_id)
        self.assertEqual(use_case_request.plan_id, expected_plan_id)

    def test_plan_id_string_with_invalid_format_raises_bad_request(self) -> None:
        plan_id = "invalid-format"
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(plan_id)
        self.assertEqual(
            err.exception.message, f"Plan id must be in UUID format, got {plan_id}."
        )


class ExpectedInputsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.expected_inputs = plan_detail_expected_input

    def test_expected_inputs_has_correct_length(self) -> None:
        assert len(self.expected_inputs) == 1

    def test_expected_input_is_of_type_path_param(self) -> None:
        assert isinstance(self.expected_inputs[0], PathParameter)

    def test_expected_input_has_correct_name(self) -> None:
        assert self.expected_inputs[0].name == "plan_id"

    def test_expected_input_has_correct_description(self) -> None:
        assert self.expected_inputs[0].description == "The plan id."
