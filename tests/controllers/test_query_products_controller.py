from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from unittest import TestCase

from arbeitszeit.use_cases import ProductFilter
from arbeitszeit_web.query_products import QueryProductsController


class QueryProductsControllerTests(TestCase):
    def setUp(self) -> None:
        self.controller = QueryProductsController()

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

    def test_that_name_choice_produces_requests_filter_by_name(self) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Name")
        )
        self.assertEqual(request.get_filter_category(), ProductFilter.by_name)

    def test_that_description_choice_products_requests_filter_by_description(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="Beschreibung")
        )
        self.assertEqual(request.get_filter_category(), ProductFilter.by_description)

    def test_that_random_string_products_requests_filter_by_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="awqwrndaj")
        )
        self.assertEqual(request.get_filter_category(), ProductFilter.by_name)


def make_fake_form(
    query: Optional[str] = None, filter_category: Optional[str] = None
) -> FakeQueryProductsForm:
    return FakeQueryProductsForm(
        query=query or "", products_filter=filter_category or "Name"
    )


@dataclass
class FakeQueryProductsForm:
    query: str
    products_filter: str

    def get_query_string(self) -> str:
        return self.query

    def get_category_string(self) -> str:
        return self.products_filter
