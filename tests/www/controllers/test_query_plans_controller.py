from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.interactors.query_plans import PlanFilter, PlanSorting
from arbeitszeit_web.www.controllers.query_plans_controller import QueryPlansController
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


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
        request = self.controller.import_form_data()
        self.assertIsNone(request.query_string)

    def test_that_empty_sorting_field_results_in_sorting_by_activation_date(
        self,
    ) -> None:
        request = self.controller.import_form_data()
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

    def test_that_empty_include_expired_plans_field_results_in_false(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertFalse(request.include_expired_plans)


class PaginationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryPlansController)

    def test_if_no_page_is_specified_in_query_args_use_offset_of_0(
        self,
    ):
        request = FakeRequest()
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 0

    def test_that_without_request_specified_the_offset_is_set_to_0(self) -> None:
        interactor_request = self.controller.import_form_data(request=None)
        assert interactor_request.offset == 0

    def test_that_page_two_has_an_offset_of_15(self) -> None:
        request = FakeRequest()
        request.set_arg(arg="page", value="2")
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 15

    def test_that_offset_0_is_assumed_if_no_valid_integer_is_specified_as_page(self):
        request = FakeRequest()
        request.set_arg(arg="page", value="123abc")
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 0

    def test_that_offset_is_150_for_page_11(self) -> None:
        request = FakeRequest()
        request.set_arg(arg="page", value="11")
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 150

    def test_that_limit_is_15(self) -> None:
        request = FakeRequest()
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.limit == 15


def make_fake_form(
    query: Optional[str] = None,
    filter_category: Optional[str] = None,
    sorting_category: Optional[str] = None,
    include_expired_plans: Optional[bool] = None,
) -> FakeQueryPlansForm:
    return FakeQueryPlansForm(
        query=query or "",
        products_filter=filter_category or "Produktname",
        sorting_category=sorting_category or "activation",
        include_expired_plans=include_expired_plans or False,
    )


@dataclass
class FakeQueryPlansForm:
    query: str
    products_filter: str
    sorting_category: str
    include_expired_plans: bool

    def get_query_string(self) -> str:
        return self.query

    def get_category_string(self) -> str:
        return self.products_filter

    def get_radio_string(self) -> str:
        return self.sorting_category

    def get_checkbox_value(self) -> bool:
        return self.include_expired_plans
