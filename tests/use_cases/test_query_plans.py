from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases import (
    PlanFilter,
    PlanQueryResponse,
    QueryPlans,
    QueryPlansRequest,
)
from tests.data_generators import PlanGenerator

from .dependency_injection import injection_test


def plan_in_results(plan: Plan, response: PlanQueryResponse) -> bool:
    return any(
        (
            plan.id == result.plan_id
            and plan.prd_name == result.product_name
            and plan.planner.id == result.company_id
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


def make_request(query: Optional[str], category: PlanFilter):
    return QueryPlansRequestTestImpl(
        query=query,
        filter_category=category,
    )


@dataclass
class QueryPlansRequestTestImpl(QueryPlansRequest):
    query: Optional[str]
    filter_category: PlanFilter

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> PlanFilter:
        return self.filter_category
