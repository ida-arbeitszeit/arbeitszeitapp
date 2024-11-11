from parameterized import parameterized

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting
from arbeitszeit_web.api.controllers.parameters import QueryParameter
from arbeitszeit_web.api.controllers.query_plans_api_controller import (
    QueryPlansApiController,
    active_plans_expected_inputs,
)
from arbeitszeit_web.api.response_errors import BadRequest
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryPlansApiController)

    def test_that_by_default_a_request_gets_returned_which_sorts_by_activation(self):
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.sorting_category, PlanSorting.by_activation)

    def test_that_by_default_a_request_gets_returned_which_filters_by_plan_id(self):
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.filter_category, PlanFilter.by_plan_id)

    def test_that_by_default_a_request_gets_returned_without_query_string(self):
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertIsNone(use_case_request.query_string)

    def test_that_by_default_a_use_case_request_with_offset_0_gets_returned_if_offset_query_string_was_empty(
        self,
    ):
        request = FakeRequest()
        assert not request.query_string().get("offset")
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.offset, 0)

    def test_that_by_default_a_use_case_request_with_limit_30_gets_returned_if_limit_query_string_was_empty(
        self,
    ):
        request = FakeRequest()
        assert not request.query_string().get("limit")
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.limit, 30)

    @parameterized.expand(
        [
            (0,),
            (110,),
        ]
    )
    def test_offset_gets_returned_if_it_is_positive_integer_and_set_in_query_string(
        self,
        expected_offset: int,
    ):
        request = FakeRequest()
        request.set_arg(arg="offset", value=str(expected_offset))
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.offset, expected_offset)

    @parameterized.expand(
        [
            (0,),
            (110,),
        ]
    )
    def test_correct_limit_gets_returned_if_it_is_positive_integer_and_set_in_query_string(
        self,
        expected_limit: int,
    ):
        request = FakeRequest()
        request.set_arg(arg="limit", value=expected_limit)
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.limit, expected_limit)

    @parameterized.expand(
        [
            (0, 110),
            (110, 0),
        ]
    )
    def test_both_correct_limit_and_offset_get_returned_if_specified_in_query_string(
        self,
        expected_limit: int,
        expected_offset: int,
    ):
        request = FakeRequest()
        request.set_arg(arg="limit", value=expected_limit)
        request.set_arg(arg="offset", value=expected_offset)
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.limit, expected_limit)
        self.assertEqual(use_case_request.offset, expected_offset)

    @parameterized.expand(
        [
            ("abc",),
            ("123abc",),
            ("abc123",),
        ]
    )
    def test_controller_raises_bad_request_if_offset_query_string_has_letters(
        self,
        offset: str,
    ):
        request = FakeRequest()
        request.set_arg(arg="offset", value=offset)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(
            err.exception.message, f"Input must be an integer, not {offset}."
        )

    def test_controller_raises_bad_request_if_offset_query_string_is_negative_number(
        self,
    ):
        request = FakeRequest()
        input = -123
        request.set_arg(arg="offset", value=input)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(
            err.exception.message, f"Input must be greater or equal zero, not {input}."
        )

    def test_controller_raises_bad_request_if_limit_query_string_has_letters(self):
        request = FakeRequest()
        input = "123abc"
        request.set_arg(arg="limit", value=input)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(
            err.exception.message, f"Input must be an integer, not {input}."
        )

    def test_controller_raises_bad_request_if_limit_query_string_is_negative_number(
        self,
    ):
        request = FakeRequest()
        input = -123
        request.set_arg(arg="limit", value=input)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(
            err.exception.message, f"Input must be greater or equal zero, not {input}."
        )


class ExpectedInputsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryPlansApiController)
        self.inputs = active_plans_expected_inputs

    def test_controller_has_two_expected_inputs(self):
        self.assertEqual(len(self.inputs), 2)

    def test_first_expected_input_is_offset(self):
        input = self.inputs[0]
        self.assertEqual(input.name, "offset")

    def test_input_offset_is_query_param(self):
        input = self.inputs[0]
        self.assertIsInstance(input, QueryParameter)

    def test_input_offset_has_correct_parameters(self):
        input = self.inputs[0]
        self.assertEqual(input.name, "offset")
        self.assertEqual(input.type, int)
        self.assertEqual(input.description, "The query offset.")
        self.assertEqual(input.default, 0)
        self.assertEqual(input.required, False)

    def test_second_expected_input_is_limit(self):
        input = self.inputs[1]
        self.assertEqual(input.name, "limit")

    def test_input_limit_is_query_param(self):
        input = self.inputs[1]
        self.assertIsInstance(input, QueryParameter)

    def test_input_limit_has_correct_parameters(self):
        input = self.inputs[1]
        self.assertEqual(input.name, "limit")
        self.assertEqual(input.type, int)
        self.assertEqual(input.description, "The query limit.")
        self.assertEqual(input.default, 30)
        self.assertEqual(input.required, False)
