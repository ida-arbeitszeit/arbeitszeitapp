from datetime import datetime, timedelta
from typing import Optional

from arbeitszeit.records import Plan
from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    PlanSorting,
    QueryPlans,
    QueryPlansRequest,
)
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_plans = self.injector.get(QueryPlans)

    def test_that_no_plan_is_returned_when_searching_an_empty_repository(self):
        response = self.query_plans(self.make_request(None, PlanFilter.by_product_name))
        assert not response.results
        response = self.query_plans(self.make_request(None, PlanFilter.by_plan_id))
        assert not response.results

    def test_that_plans_where_id_is_exact_match_are_returned(self):
        expected_plan = self.plan_generator.create_plan()
        query = str(expected_plan.id)
        response = self.query_plans(self.make_request(query, PlanFilter.by_plan_id))
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_id_returns_correct_result(self):
        expected_plan = self.plan_generator.create_plan()
        substring_query = str(expected_plan.id)[5:10]
        response = self.query_plans(
            self.make_request(substring_query, PlanFilter.by_plan_id)
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_that_plans_where_product_name_is_exact_match_are_returned(self):
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "Name XYZ"
        response = self.query_plans(
            self.make_request(query, PlanFilter.by_product_name)
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_product_name_returns_correct_result(self):
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "me X"
        response = self.query_plans(
            self.make_request(query, PlanFilter.by_product_name)
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_product_is_case_insensitive(self):
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "xyz"
        response = self.query_plans(
            self.make_request(query, PlanFilter.by_product_name)
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_that_plans_are_returned_in_order_of_activation_when_requested_with_newest_plan_first(
        self,
    ):
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        expected_third = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        expected_second = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        expected_first = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        response = self.query_plans(
            self.make_request(sorting=PlanSorting.by_activation)
        )
        assert response.results[0].plan_id == expected_first.id
        assert response.results[1].plan_id == expected_second.id
        assert response.results[2].plan_id == expected_third.id

    def test_that_plans_are_returned_in_order_of_company_name_when_requested(self):
        for name in ["c_name", "a_name", "B_name"]:
            self.plan_generator.create_plan(
                planner=self.company_generator.create_company(name=name),
            )
        response = self.query_plans(
            self.make_request(sorting=PlanSorting.by_company_name)
        )
        assert response.results[0].company_name == "a_name"
        assert response.results[1].company_name == "B_name"
        assert response.results[2].company_name == "c_name"

    def test_that_filtered_plans_by_name_are_returned_in_order_of_activation(self):
        self.datetime_service.freeze_time(datetime(2000, 1, 4))
        expected_second = self.plan_generator.create_plan(product_name="abcde")
        self.datetime_service.advance_time(timedelta(days=1))
        expected_first = self.plan_generator.create_plan(product_name="xyabc")
        self.datetime_service.advance_time(timedelta(days=1))
        # unexpected plan
        self.plan_generator.create_plan(
            product_name="cba",
        )
        response = self.query_plans(
            self.make_request(
                sorting=PlanSorting.by_activation,
                category=PlanFilter.by_product_name,
                query="abc",
            )
        )
        assert len(response.results) == 2
        assert response.results[0].plan_id == expected_first.id
        assert response.results[1].plan_id == expected_second.id

    def test_that_correct_price_per_unit_of_zero_is_displayed_for_a_public_plan(self):
        self.plan_generator.create_plan(is_public_service=True)
        response = self.query_plans(self.make_request())
        assert response.results[0].price_per_unit == 0

    def test_that_price_of_cooperating_plans_is_correctly_displayed(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        plan1 = self.plan_generator.create_plan(cooperation=cooperation, amount=1000)
        plan2 = self.plan_generator.create_plan(cooperation=cooperation, amount=1)
        response = self.query_plans(
            self.make_request(sorting=PlanSorting.by_activation)
        )
        assert response.results[0].price_per_unit == self.price_checker.get_unit_price(
            plan1.id
        )
        assert response.results[1].price_per_unit == self.price_checker.get_unit_price(
            plan2.id
        )

    def test_that_total_results_is_1_if_one_plan_is_present(
        self,
    ):
        self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        self.assertEqual(response.total_results, 1)

    def test_that_total_results_is_6_if_six_plans_are_present(
        self,
    ):
        for _ in range(6):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        assert response.total_results == 6

    def test_that_first_10_plans_are_returned_if_limit_is_10(
        self,
    ):
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request(limit=10))
        assert len(response.results) == 10

    def test_that_all_plans_are_returned_if_limit_is_0_and_there_are_20_plans(
        self,
    ):
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        assert len(response.results) == 20

    def test_that_5_plans_are_returned_on_second_page_if_20_plans_exist_and_offset_is_15(
        self,
    ):
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request(offset=15))
        assert len(response.results) == 5

    def test_that_a_plan_awaiting_approval_is_not_returned(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(approved=False, planner=planner)
        response = self.query_plans(self.make_request())
        assert not response.results

    def make_request(
        self,
        query: Optional[str] = None,
        category: Optional[PlanFilter] = None,
        sorting: Optional[PlanSorting] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        return QueryPlansRequest(
            query_string=query or "",
            filter_category=category or PlanFilter.by_product_name,
            sorting_category=sorting or PlanSorting.by_activation,
            offset=offset,
            limit=limit,
        )

    def assertPlanInResults(self, plan: Plan, response: PlanQueryResponse) -> bool:
        return any(
            (
                plan.id == result.plan_id
                and plan.prd_name == result.product_name
                and plan.planner == result.company_id
                and plan.activation_date == result.activation_date
                for result in response.results
            )
        )
