from arbeitszeit.use_cases.query_companies import CompanyFilter
from arbeitszeit_web.api.controllers.parameters import QueryParameter
from arbeitszeit_web.api.controllers.query_companies_api_controller import (
    QueryCompaniesApiController,
    query_companies_expected_inputs,
)
from arbeitszeit_web.api.response_errors import BadRequest
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryCompaniesApiController)

    def test_that_by_default_a_request_gets_returned_which_filters_by_company_name(
        self,
    ) -> None:
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.filter_category, CompanyFilter.by_name)

    def test_that_by_default_a_request_gets_returned_without_query_string(self) -> None:
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertIsNone(use_case_request.query_string)

    def test_that_by_default_a_use_case_request_with_offset_0_gets_returned_if_offset_query_string_was_empty(
        self,
    ):
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.offset, 0)

    def test_that_by_default_a_use_case_request_with_limit_30_gets_returned_if_limit_query_string_was_empty(
        self,
    ) -> None:
        request = FakeRequest()
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.limit, 30)

    def test_correct_offset_gets_returned_if_it_was_set_in_query_string(self) -> None:
        request = FakeRequest()
        expected_offset = 8
        request.set_arg(arg="offset", value=str(expected_offset))
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.offset, expected_offset)

    def test_correct_limit_gets_returned_if_it_was_set_in_query_string(self) -> None:
        request = FakeRequest()
        expected_limit = 7
        request.set_arg(arg="limit", value=expected_limit)
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.limit, expected_limit)

    def test_both_correct_limit_and_offset_get_returned_if_specified_in_query_string(
        self,
    ) -> None:
        request = FakeRequest()
        expected_limit = 7
        request.set_arg(arg="limit", value=expected_limit)
        expected_offset = 8
        request.set_arg(arg="offset", value=str(expected_offset))
        use_case_request = self.controller.create_request(request)
        self.assertEqual(use_case_request.limit, expected_limit)
        self.assertEqual(use_case_request.offset, expected_offset)

    def test_controller_raises_bad_request_if_offset_query_string_has_letters(self):
        request = FakeRequest()
        input = "123abc"
        request.set_arg(arg="offset", value=input)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(
            err.exception.message, f"Input must be an integer, not {input}."
        )

    def test_controller_raises_bad_request_if_offset_query_string_is_negative_number(
        self,
    ):
        request = FakeRequest()
        input = "-123"
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
        input = "-123"
        request.set_arg(arg="limit", value=input)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        self.assertEqual(
            err.exception.message, f"Input must be greater or equal zero, not {input}."
        )


class ExpectedInputsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryCompaniesApiController)
        self.inputs = query_companies_expected_inputs

    def test_controller_has_two_expected_inputs(self) -> None:
        self.assertEqual(len(self.inputs), 2)

    def test_first_expected_input_is_offset(self) -> None:
        input = self.inputs[0]
        self.assertEqual(input.name, "offset")

    def test_input_offset_is_query_param(self) -> None:
        input = self.inputs[0]
        self.assertIsInstance(input, QueryParameter)

    def test_input_offset_has_correct_parameters(self) -> None:
        input = self.inputs[0]
        self.assertEqual(input.name, "offset")
        self.assertEqual(input.type, int)
        self.assertEqual(input.description, "The query offset.")
        self.assertEqual(input.default, 0)
        self.assertEqual(input.required, False)

    def test_second_expected_input_is_limit(self) -> None:
        input = self.inputs[1]
        self.assertEqual(input.name, "limit")

    def test_input_limit_is_query_param(self) -> None:
        input = self.inputs[1]
        self.assertIsInstance(input, QueryParameter)

    def test_input_limit_has_correct_parameters(self) -> None:
        input = self.inputs[1]
        self.assertEqual(input.name, "limit")
        self.assertEqual(input.type, int)
        self.assertEqual(input.description, "The query limit.")
        self.assertEqual(input.default, 30)
        self.assertEqual(input.required, False)
