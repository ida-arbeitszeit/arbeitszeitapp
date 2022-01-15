from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from unittest import TestCase

from arbeitszeit.use_cases import PlanFilter
from arbeitszeit_web.query_plans import QueryPlansController


class QueryPlansControllerTests(TestCase):
    def setUp(self) -> None:
        self.controller = QueryPlansController()

    def test_that_empty_query_string_translates_to_no_query_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query=""))
        self.assertTrue(request.get_query_string() is None)

    def test_that_a_query_string_is_taken_as_the_literal_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query="test"))
        self.assertEqual(request.get_query_string(), "test")

    def test_that_leading_and_trailing_whitespaces_are_ignored(self) -> None:
        request = self.controller.import_form_data(make_fake_form(query=" test  "))
        self.assertEqual(request.get_query_string(), "test")
        request = self.controller.import_form_data(make_fake_form(query="   "))
        self.assertTrue(request.get_query_string() is None)

    def test_that_plan_id_choice_produces_requests_filter_by_plan_id(self) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Plan-ID")
        )
        self.assertEqual(request.get_filter_category(), PlanFilter.by_plan_id)

    def test_that_product_name_choice_produces_requests_filter_by_product_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Produktname")
        )
        self.assertEqual(request.get_filter_category(), PlanFilter.by_product_name)

    def test_that_random_string_produces_requests_filter_by_plan_id(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="awqwrndaj")
        )
        self.assertEqual(request.get_filter_category(), PlanFilter.by_product_name)

    def test_that_default_request_model_includes_no_search_query(
        self,
    ) -> None:
        request = self.controller.import_form_data(form=None)
        self.assertTrue(request.get_query_string() is None)


def make_fake_form(
    query: Optional[str] = None, filter_category: Optional[str] = None
) -> FakeQueryPlansForm:
    return FakeQueryPlansForm(
        query=query or "", products_filter=filter_category or "Produktname"
    )


@dataclass
class FakeQueryPlansForm:
    query: str
    products_filter: str

    def get_query_string(self) -> str:
        return self.query

    def get_category_string(self) -> str:
        return self.products_filter
