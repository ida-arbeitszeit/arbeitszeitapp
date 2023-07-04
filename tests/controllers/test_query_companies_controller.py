from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.query_companies import CompanyFilter
from arbeitszeit_web.www.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from tests.controllers.base_test_case import BaseTestCase
from tests.request import FakeRequest


class QueryCompaniesControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryCompaniesController)

    def test_that_empty_query_string_translates_to_no_query_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query=""))
        self.assertIsNone(request.get_query_string())

    def test_that_a_query_string_is_taken_as_the_literal_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query="test"))
        self.assertEqual(request.get_query_string(), "test")

    def test_that_leading_and_trailing_whitespaces_are_ignored(self) -> None:
        request = self.controller.import_form_data(make_fake_form(query=" test  "))
        self.assertEqual(request.get_query_string(), "test")
        request = self.controller.import_form_data(make_fake_form(query="   "))
        self.assertIsNone(request.get_query_string())

    def test_that_name_choice_produces_requests_filter_by_company_name(self) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Name")
        )
        self.assertEqual(request.get_filter_category(), CompanyFilter.by_name)

    def test_that_email_choice_produces_requests_filter_by_email(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Email")
        )
        self.assertEqual(request.get_filter_category(), CompanyFilter.by_email)

    def test_that_random_string_produces_requests_filter_by_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="awqwrndaj")
        )
        self.assertEqual(request.get_filter_category(), CompanyFilter.by_name)

    def test_that_default_request_model_includes_no_search_query(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertIsNone(request.get_query_string())


class PaginationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryCompaniesController)
        self.request = self.injector.get(FakeRequest)

    def test_if_no_page_is_specified_in_query_args_use_offset_of_0(
        self,
    ):
        use_case_request = self.controller.import_form_data()
        assert use_case_request.get_offset() == 0

    def test_that_without_request_specified_the_offset_is_set_to_0(self) -> None:
        use_case_request = self.controller.import_form_data()
        assert use_case_request.get_offset() == 0

    def test_that_page_two_has_an_offset_of_15(self) -> None:
        self.request.set_arg(arg="page", value="2")
        use_case_request = self.controller.import_form_data()
        assert use_case_request.get_offset() == 15

    def test_that_offset_0_is_assumed_if_no_valid_integer_is_specified_as_page(self):
        self.request.set_arg(arg="page", value="123abc")
        use_case_request = self.controller.import_form_data()
        assert use_case_request.get_offset() == 0

    def test_that_offset_is_150_for_page_11(self) -> None:
        self.request.set_arg(arg="page", value="11")
        use_case_request = self.controller.import_form_data()
        assert use_case_request.get_offset() == 150

    def test_that_limit_is_15(self) -> None:
        use_case_request = self.controller.import_form_data()
        assert use_case_request.get_limit() == 15


def make_fake_form(
    query: Optional[str] = None, filter_category: Optional[str] = None
) -> FakeQueryCompaniesForm:
    return FakeQueryCompaniesForm(query=query or "", filter=filter_category or "Name")


@dataclass
class FakeQueryCompaniesForm:
    query: str
    filter: str

    def get_query_string(self) -> str:
        return self.query

    def get_category_string(self) -> str:
        return self.filter
