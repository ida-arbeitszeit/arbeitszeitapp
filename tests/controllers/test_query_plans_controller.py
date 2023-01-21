from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases import PlanFilter
from arbeitszeit.use_cases.query_plans import PlanSorting
from arbeitszeit_web.query_plans import NotAnIntegerError, QueryPlansController
from tests.controllers.base_test_case import BaseTestCase
from tests.request import FakeRequest


class QueryPlansControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryPlansController)

    def test_that_empty_query_string_translates_to_no_query_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query=""))
        self.assertIsNone(request.query_string)

    def test_that_a_query_string_is_taken_as_the_literal_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query="test"))
        self.assertEqual(request.query_string, "test")

    def test_that_leading_and_trailing_whitespaces_are_ignored(self) -> None:
        request = self.controller.import_form_data(make_fake_form(query=" test  "))
        self.assertEqual(request.query_string, "test")
        request = self.controller.import_form_data(make_fake_form(query="   "))
        self.assertIsNone(request.query_string)

    def test_that_plan_id_choice_produces_requests_filter_by_plan_id(self) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Plan-ID")
        )
        self.assertEqual(request.filter_category, PlanFilter.by_plan_id)

    def test_that_product_name_choice_produces_requests_filter_by_product_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Produktname")
        )
        self.assertEqual(request.filter_category, PlanFilter.by_product_name)

    def test_that_random_string_produces_requests_filter_by_plan_id(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="awqwrndaj")
        )
        self.assertEqual(request.filter_category, PlanFilter.by_product_name)

    def test_that_default_request_model_includes_no_search_query(
        self,
    ) -> None:
        request = self.controller.import_form_data(form=None)
        self.assertIsNone(request.query_string)

    def test_that_empty_sorting_field_results_in_sorting_by_activation_date(
        self,
    ) -> None:
        request = self.controller.import_form_data(form=None)
        self.assertEqual(request.sorting_category, PlanSorting.by_activation)

    def test_that_nonexisting_sorting_field_results_in_sorting_by_activation_date(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            form=make_fake_form(sorting_category="somethingjsbjbsd")
        )
        self.assertEqual(request.sorting_category, PlanSorting.by_activation)

    def test_that_company_name_in_sorting_field_results_in_sorting_by_company_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            form=make_fake_form(sorting_category="company_name")
        )
        self.assertEqual(request.sorting_category, PlanSorting.by_company_name)

    def test_that_price_in_sorting_field_results_in_sorting_by_price(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            form=make_fake_form(sorting_category="price")
        )
        self.assertEqual(request.sorting_category, PlanSorting.by_price)


class PaginationTests(BaseTestCase):
    def test_no_page_is_passed_to_use_case_request_if_none_was_given_in_request_query(
        self,
    ):
        request = FakeRequest()
        controller = QueryPlansController(request=request)
        use_case_request = controller.import_form_data(form=None)
        self.assertIsNone(use_case_request.page)

    def test_error_is_raised_if_request_has_invalid_page_parameter(self):
        request = FakeRequest()
        request.set_arg(arg="page", value="123abc")
        controller = QueryPlansController(request=request)
        with self.assertRaises(NotAnIntegerError):
            controller.import_form_data(form=None)

    def test_request_page_parameter_gets_passed_to_use_case_request(self):
        request = FakeRequest()
        request.set_arg(arg="page", value="123")
        controller = QueryPlansController(request=request)
        use_case_request = controller.import_form_data(form=None)
        self.assertEqual(use_case_request.page, 123)


def make_fake_form(
    query: Optional[str] = None,
    filter_category: Optional[str] = None,
    sorting_category: Optional[str] = None,
) -> FakeQueryPlansForm:
    return FakeQueryPlansForm(
        query=query or "",
        products_filter=filter_category or "Produktname",
        sorting_category=sorting_category or "activation",
    )


@dataclass
class FakeQueryPlansForm:
    query: str
    products_filter: str
    sorting_category: str

    def get_query_string(self) -> str:
        return self.query

    def get_category_string(self) -> str:
        return self.products_filter

    def get_radio_string(self) -> str:
        return self.sorting_category
