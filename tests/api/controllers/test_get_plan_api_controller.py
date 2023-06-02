from uuid import uuid4

from arbeitszeit_web.api_controllers.get_plan_api_controller import GetPlanApiController
from arbeitszeit_web.api_presenters.response_errors import BadRequest
from tests.controllers.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(GetPlanApiController)

    def test_plan_id_string_in_uuid_format_gets_converted_to_uuid(self) -> None:
        expected_response = uuid4()
        plan_id = str(expected_response)
        response = self.controller.format_input(plan_id)
        self.assertEqual(response, expected_response)

    def test_plan_id_string_in_uuid_format_with_whitespace_gets_converted_to_uuid(
        self,
    ) -> None:
        expected_response = uuid4()
        plan_id = f"  {expected_response}  "
        response = self.controller.format_input(plan_id)
        self.assertEqual(response, expected_response)

    def test_plan_id_string_with_invalid_format_raises_bad_request(self) -> None:
        plan_id = "invalid-format"
        with self.assertRaises(BadRequest) as err:
            self.controller.format_input(plan_id)
        self.assertEqual(
            err.exception.message, f"Plan id must be in UUID format, got {plan_id}."
        )
