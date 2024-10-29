from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum, auto
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    PlanSorting,
    QueryPlans,
    QueryPlansRequest,
)
from tests.use_cases.base_test_case import BaseTestCase


class SearchStrategy(Enum):
    by_id_sort_by_date_exclude_expired = auto()
    by_id_sort_by_date_include_expired = auto()
    by_id_sort_by_name_exclude_expired = auto()
    by_id_sort_by_name_include_expired = auto()
    by_name_sort_by_date_exclude_expired = auto()
    by_name_sort_by_date_include_expired = auto()
    by_name_sort_by_name_exclude_expired = auto()
    by_name_sort_by_name_include_expired = auto()


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_plans = self.injector.get(QueryPlans)

    @parameterized.expand([(strategy,) for strategy in SearchStrategy])
    def test_that_no_plan_is_returned_when_searching_an_empty_repository(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        response = self.query_plans(self.make_request(search_strategy))
        assert not response.results

    @parameterized.expand([(strategy,) for strategy in SearchStrategy])
    def test_that_a_plan_awaiting_approval_is_not_returned(
        self,
        strategy: SearchStrategy,
    ) -> None:
        self.plan_generator.create_plan(approved=False)
        response = self.query_plans(self.make_request(strategy))
        assert not response.results

    @parameterized.expand([(strategy,) for strategy in SearchStrategy])
    def test_that_all_active_plans_are_returned(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        expected_number_of_plans = 3
        for _ in range(expected_number_of_plans):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request(search_strategy))
        assert len(response.results) == expected_number_of_plans

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_exclude_expired,),
            (SearchStrategy.by_name_sort_by_date_exclude_expired,),
            (SearchStrategy.by_id_sort_by_name_exclude_expired,),
            (SearchStrategy.by_name_sort_by_name_exclude_expired,),
        ]
    )
    def test_that_no_expired_plans_are_returned_when_they_are_excluded(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        expected_number_of_plans = 0
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        for _ in range(3):
            self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.query_plans(self.make_request(search_strategy))
        assert len(response.results) == expected_number_of_plans

    def test_that_only_active_plan_is_returned_when_expired_plans_are_excluded(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        expected_plan = self.plan_generator.create_plan()
        response = self.query_plans(
            self.make_request(SearchStrategy.by_id_sort_by_date_exclude_expired)
        )
        assert len(response.results) == 1
        assert self.assertPlanInResults(expected_plan, response)

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_include_expired,),
            (SearchStrategy.by_name_sort_by_date_include_expired,),
            (SearchStrategy.by_id_sort_by_name_include_expired,),
            (SearchStrategy.by_name_sort_by_name_include_expired,),
        ]
    )
    def test_that_expired_plans_are_returned_when_they_are_included(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        expected_number_of_plans = 3
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        for _ in range(expected_number_of_plans):
            self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.query_plans(self.make_request(search_strategy))
        assert len(response.results) == expected_number_of_plans

    def test_that_expired_plan_is_shown_as_expired(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.query_plans(
            self.make_request(SearchStrategy.by_id_sort_by_date_include_expired)
        )
        assert response.results[0].is_expired

    def test_that_active_plan_is_not_shown_as_expired(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        assert not response.results[0].is_expired

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_exclude_expired,),
            (SearchStrategy.by_id_sort_by_date_include_expired,),
            (SearchStrategy.by_id_sort_by_name_exclude_expired,),
            (SearchStrategy.by_id_sort_by_name_include_expired,),
        ]
    )
    def test_that_active_plan_where_id_is_exact_match_is_returned(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        self.plan_generator.create_plan()
        expected_plan = self.plan_generator.create_plan()
        response = self.query_plans(
            self.make_request(search_strategy=search_strategy, query=str(expected_plan))
        )
        assert len(response.results) == 1
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_id_returns_correct_plan(self) -> None:
        expected_plan = self.plan_generator.create_plan()
        substring_query = str(expected_plan)[5:10]
        response = self.query_plans(
            self.make_request(
                search_strategy=SearchStrategy.by_id_sort_by_date_exclude_expired,
                query=substring_query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_that_plans_where_product_name_is_exact_match_are_returned(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "Name XYZ"
        response = self.query_plans(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query=query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_product_name_returns_correct_result(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "me X"
        response = self.query_plans(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query=query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_product_is_case_insensitive(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "xyz"
        response = self.query_plans(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query=query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_exclude_expired,),
            (SearchStrategy.by_id_sort_by_date_include_expired,),
            (SearchStrategy.by_name_sort_by_date_exclude_expired,),
            (SearchStrategy.by_name_sort_by_date_include_expired,),
        ]
    )
    def test_that_plans_are_returned_in_order_of_activation_with_newest_plan_first_when_requested(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        expected_third = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        expected_second = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        expected_first = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        response = self.query_plans(self.make_request(search_strategy=search_strategy))
        assert response.results[0].plan_id == expected_first
        assert response.results[1].plan_id == expected_second
        assert response.results[2].plan_id == expected_third

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_name_exclude_expired,),
            (SearchStrategy.by_id_sort_by_name_include_expired,),
            (SearchStrategy.by_name_sort_by_name_exclude_expired,),
            (SearchStrategy.by_name_sort_by_name_include_expired,),
        ]
    )
    def test_that_plans_are_returned_sorted_by_company_name_when_requested(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        for name in ["c_name", "a_name", "B_name"]:
            self.plan_generator.create_plan(
                planner=self.company_generator.create_company(name=name),
            )
        response = self.query_plans(self.make_request(search_strategy=search_strategy))
        assert response.results[0].company_name == "a_name"
        assert response.results[1].company_name == "B_name"
        assert response.results[2].company_name == "c_name"

    @parameterized.expand(
        [
            (SearchStrategy.by_name_sort_by_date_exclude_expired,),
            (SearchStrategy.by_name_sort_by_date_include_expired,),
        ]
    )
    def test_that_plans_filtered_by_name_are_returned_sorted_by_date_if_requested(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
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
                search_strategy=search_strategy,
                query="abc",
            )
        )
        assert len(response.results) == 2
        assert response.results[0].plan_id == expected_first
        assert response.results[1].plan_id == expected_second

    def test_that_correct_price_per_unit_of_zero_is_displayed_for_a_public_plan(
        self,
    ) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        response = self.query_plans(self.make_request())
        assert response.results[0].price_per_unit == 0

    def test_that_labour_per_unit_is_correctly_displayed(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(200),
                resource_cost=Decimal(100),
                means_cost=Decimal(50),
            )
        )
        response = self.query_plans(self.make_request())
        queried_plan = response.results[0]
        assert (
            queried_plan.labour_cost_per_unit
            == self.price_checker.get_labour_per_unit(plan)
        )

    def test_that_two_cooperating_plans_have_the_same_price(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(cooperation=cooperation, amount=1000)
        self.plan_generator.create_plan(cooperation=cooperation, amount=1)
        response = self.query_plans(self.make_request())
        assert response.results[0].price_per_unit == response.results[1].price_per_unit

    def test_that_price_of_cooperating_plans_is_correct(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        plan1 = self.plan_generator.create_plan(
            cooperation=cooperation,
            amount=1000,
        )
        plan2 = self.plan_generator.create_plan(
            cooperation=cooperation,
            amount=1,
        )
        response = self.query_plans(self.make_request())
        assert response.results[0].price_per_unit == self.price_checker.get_unit_price(
            plan1
        )
        assert response.results[1].price_per_unit == self.price_checker.get_unit_price(
            plan2
        )

    def test_that_total_results_is_1_if_one_plan_is_present(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        self.assertEqual(response.total_results, 1)

    def test_that_total_results_is_6_if_six_plans_are_present(
        self,
    ) -> None:
        for _ in range(6):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        assert response.total_results == 6

    def test_that_first_10_plans_are_returned_if_limit_is_10(
        self,
    ) -> None:
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request(limit=10))
        assert len(response.results) == 10

    def test_that_all_plans_are_returned_if_limit_is_0_and_there_are_20_plans(
        self,
    ) -> None:
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request())
        assert len(response.results) == 20

    def test_that_5_plans_are_returned_on_second_page_if_20_plans_exist_and_offset_is_15(
        self,
    ) -> None:
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.query_plans(self.make_request(offset=15))
        assert len(response.results) == 5

    def make_request(
        self,
        search_strategy: SearchStrategy | None = None,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> QueryPlansRequest:
        if search_strategy is None:
            search_strategy = SearchStrategy.by_name_sort_by_date_exclude_expired
        match search_strategy:
            case SearchStrategy.by_id_sort_by_date_exclude_expired:
                category = PlanFilter.by_plan_id
                sorting = PlanSorting.by_activation
                include_expired_plans = False
            case SearchStrategy.by_id_sort_by_date_include_expired:
                category = PlanFilter.by_plan_id
                sorting = PlanSorting.by_activation
                include_expired_plans = True
            case SearchStrategy.by_id_sort_by_name_exclude_expired:
                category = PlanFilter.by_plan_id
                sorting = PlanSorting.by_company_name
                include_expired_plans = False
            case SearchStrategy.by_id_sort_by_name_include_expired:
                category = PlanFilter.by_plan_id
                sorting = PlanSorting.by_company_name
                include_expired_plans = True
            case SearchStrategy.by_name_sort_by_date_exclude_expired:
                category = PlanFilter.by_product_name
                sorting = PlanSorting.by_activation
                include_expired_plans = False
            case SearchStrategy.by_name_sort_by_date_include_expired:
                category = PlanFilter.by_product_name
                sorting = PlanSorting.by_activation
                include_expired_plans = True
            case SearchStrategy.by_name_sort_by_name_exclude_expired:
                category = PlanFilter.by_product_name
                sorting = PlanSorting.by_company_name
                include_expired_plans = False
            case SearchStrategy.by_name_sort_by_name_include_expired:
                category = PlanFilter.by_product_name
                sorting = PlanSorting.by_company_name
                include_expired_plans = True
        return QueryPlansRequest(
            query_string=query,
            filter_category=category,
            sorting_category=sorting,
            offset=offset,
            limit=limit,
            include_expired_plans=include_expired_plans,
        )

    def assertPlanInResults(self, plan: UUID, response: PlanQueryResponse) -> bool:
        return any((plan == result.plan_id for result in response.results))
