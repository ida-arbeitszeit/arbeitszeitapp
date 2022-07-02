from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from arbeitszeit.entities import Plan, ProductionCosts
from arbeitszeit.use_cases import (
    PlanFilter,
    PlanQueryResponse,
    QueryPlans,
    QueryPlansRequest,
)
from arbeitszeit.use_cases.query_plans import PlanSorting
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


def plan_in_results(plan: Plan, response: PlanQueryResponse) -> bool:
    return any(
        (
            plan.id == result.plan_id
            and plan.prd_name == result.product_name
            and plan.planner.id == result.company_id
            and plan.activation_date == result.activation_date
            for result in response.results
        )
    )


@injection_test
def test_that_no_plan_is_returned_when_searching_an_empty_repository(
    query_plans: QueryPlans,
):
    response = query_plans(make_request(None, PlanFilter.by_product_name))
    assert not response.results
    response = query_plans(make_request(None, PlanFilter.by_plan_id))
    assert not response.results


@injection_test
def test_that_only_active_plans_are_returned_where_plan_id_query_is_none(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(activation_date=datetime.min)
    unexpected_plan = plan_generator.create_plan(activation_date=None)
    response = query_plans(make_request(None, PlanFilter.by_plan_id))
    assert plan_in_results(expected_plan, response)
    assert not plan_in_results(unexpected_plan, response)


@injection_test
def test_that_only_active_plans_are_returned_where_product_name_query_is_none(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(activation_date=datetime.min)
    unexpected_plan = plan_generator.create_plan(activation_date=None)
    response = query_plans(make_request(None, PlanFilter.by_product_name))
    assert plan_in_results(expected_plan, response)
    assert not plan_in_results(unexpected_plan, response)


@injection_test
def test_that_plans_where_id_is_exact_match_are_returned(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(activation_date=datetime.min)
    query = str(expected_plan.id)
    response = query_plans(make_request(query, PlanFilter.by_plan_id))
    assert plan_in_results(expected_plan, response)


@injection_test
def test_query_with_substring_of_id_returns_correct_result(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(activation_date=datetime.min)
    substring_query = str(expected_plan.id)[5:10]
    response = query_plans(make_request(substring_query, PlanFilter.by_plan_id))
    assert plan_in_results(expected_plan, response)


@injection_test
def test_that_plans_where_product_name_is_exact_match_are_returned(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(
        product_name="Name XYZ", activation_date=datetime.min
    )
    query = "Name XYZ"
    response = query_plans(make_request(query, PlanFilter.by_product_name))
    assert plan_in_results(expected_plan, response)


@injection_test
def test_query_with_substring_of_product_name_returns_correct_result(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(
        product_name="Name XYZ", activation_date=datetime.min
    )
    query = "me X"
    response = query_plans(make_request(query, PlanFilter.by_product_name))
    assert plan_in_results(expected_plan, response)


@injection_test
def test_query_with_substring_of_product_is_case_insensitive(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    expected_plan = plan_generator.create_plan(
        product_name="Name XYZ", activation_date=datetime.min
    )
    query = "xyz"
    response = query_plans(make_request(query, PlanFilter.by_product_name))
    assert plan_in_results(expected_plan, response)


@injection_test
def test_that_plans_are_returned_in_order_of_activation_when_requested_with_newest_plan_first(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    expected_second = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_20_hours()
    )
    expected_first = plan_generator.create_plan(activation_date=datetime_service.now())
    expected_third = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_two_days()
    )
    response = query_plans(make_request(sorting=PlanSorting.by_activation))
    assert response.results[0].plan_id == expected_first.id
    assert response.results[1].plan_id == expected_second.id
    assert response.results[2].plan_id == expected_third.id


@injection_test
def test_that_plans_are_returned_in_order_of_price_when_requested_with_cheapest_product_first(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    expected_second = plan_generator.create_plan(
        activation_date=datetime_service.now(),
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
    )
    expected_first = plan_generator.create_plan(
        activation_date=datetime_service.now(),
        costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
    )
    expected_third = plan_generator.create_plan(
        activation_date=datetime_service.now(),
        costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
    )
    response = query_plans(make_request(sorting=PlanSorting.by_price))
    assert response.results[0].plan_id == expected_first.id
    assert response.results[1].plan_id == expected_second.id
    assert response.results[2].plan_id == expected_third.id


@injection_test
def test_that_plans_are_returned_in_order_of_company_name_when_requested(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    company_generator: CompanyGenerator,
):
    for name in ["c_name", "a_name", "B_name"]:
        plan_generator.create_plan(
            activation_date=datetime_service.now(),
            planner=company_generator.create_company(name=name),
        )
    response = query_plans(make_request(sorting=PlanSorting.by_company_name))
    assert response.results[0].company_name == "a_name"
    assert response.results[1].company_name == "B_name"
    assert response.results[2].company_name == "c_name"


@injection_test
def test_that_filtered_plans_by_name_are_returned_in_order_of_activation(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    expected_second = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_20_hours(), product_name="abcde"
    )
    expected_first = plan_generator.create_plan(
        activation_date=datetime_service.now(), product_name="xyabc"
    )
    # unexpected plan
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_two_days(), product_name="cba"
    )
    response = query_plans(
        make_request(
            sorting=PlanSorting.by_activation,
            category=PlanFilter.by_product_name,
            query="abc",
        )
    )
    assert len(response.results) == 2
    assert response.results[0].plan_id == expected_first.id
    assert response.results[1].plan_id == expected_second.id


@injection_test
def test_that_correct_price_per_unit_of_zero_is_displayed_for_a_public_plan(
    query_plans: QueryPlans,
    plan_generator: PlanGenerator,
):
    plan_generator.create_plan(is_public_service=True, activation_date=datetime.min)
    response = query_plans(make_request())
    assert response.results[0].price_per_unit == 0


def make_request(
    query: Optional[str] = None,
    category: PlanFilter = None,
    sorting: PlanSorting = None,
):
    return QueryPlansRequestTestImpl(
        query=query or "",
        filter_category=category or PlanFilter.by_product_name,
        sorting_category=sorting or PlanSorting.by_activation,
    )


@dataclass
class QueryPlansRequestTestImpl(QueryPlansRequest):
    query: Optional[str]
    filter_category: PlanFilter
    sorting_category: PlanSorting

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> PlanFilter:
        return self.filter_category

    def get_sorting_category(self) -> PlanSorting:
        return self.sorting_category
