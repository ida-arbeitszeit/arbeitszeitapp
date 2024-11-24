from parameterized import parameterized

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

    @parameterized.expand(
        [
            ([], 30, 0),
            ([("limit", "7")], 7, 0),
            ([("offset", "8")], 30, 8),
            ([("limit", "7"), ("offset", "8")], 7, 8),
        ]
    )
    def test_that_setting_the_limit_and_offset_query_params_produces_expected_limit_and_offset_in_request(
        self,
        query_string: list[tuple[str, str]],
        expected_limit: int,
        expected_offset: int,
    ) -> None:
        request = FakeRequest(query_string=query_string)
        use_case_request = self.controller.create_request(request)
        assert use_case_request.limit == expected_limit
        assert use_case_request.offset == expected_offset

    @parameterized.expand(
        [
            ([("offset", "-123")], "Input must be greater or equal zero, not -123."),
            ([("offset", "123abc")], "Input must be an integer, not 123abc."),
            ([("limit", "123abc")], "Input must be an integer, not 123abc."),
            ([("limit", "-123")], "Input must be greater or equal zero, not -123."),
        ]
    )
    def test_controller_raises_bad_request_if_limit_or_offset_are_set_incorrectly(
        self, query_string: list[tuple[str, str]], expected_error_message: str
    ) -> None:
        request = FakeRequest(query_string=query_string)
        with self.assertRaises(BadRequest) as err:
            self.controller.create_request(request)
        assert err.exception.message == expected_error_message


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
