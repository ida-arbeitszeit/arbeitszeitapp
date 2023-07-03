from uuid import uuid4

from arbeitszeit_web.api.controllers.get_plan_api_controller import GetPlanApiController
from arbeitszeit_web.api.presenters.response_errors import BadRequest
from tests.controllers.base_test_case import BaseTestCase


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
