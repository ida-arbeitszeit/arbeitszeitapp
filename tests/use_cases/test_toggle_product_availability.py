from uuid import UUID, uuid4

from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanSorting,
    QueryPlans,
    QueryPlansRequest,
)
from arbeitszeit.use_cases.toggle_product_availablity import ToggleProductAvailability

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.toggle = self.injector.get(ToggleProductAvailability)
        self.query_plans_use_case = self.injector.get(QueryPlans)

    def test_that_toggle_is_unsuccessful_when_plan_does_not_exist(self) -> None:
        response = self.toggle(uuid4(), uuid4())
        assert not response.is_success

    def test_that_toggle_is_unsuccessful_when_current_user_is_not_planner(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.toggle(uuid4(), plan)
        assert not response.is_success

    def test_that_toggling_returns_success_when_plan_exists_and_planner_is_current_user(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        response = self.toggle(planner, plan)
        assert response.is_success

    def test_that_toggling_changes_availability_to_true(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_available=False, planner=planner)
        self.toggle(planner, plan)
        assert self.is_product_available(plan)

    def test_that_toggling_changes_availability_to_false(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_available=True, planner=planner)
        self.toggle(planner, plan)
        assert not self.is_product_available(plan)

    def is_product_available(self, plan: UUID) -> bool:
        request = QueryPlansRequest(
            query_string=str(plan),
            filter_category=PlanFilter.by_plan_id,
            # The following choice is arbitrary. The concrete sorting of the
            # results does not matter.
            sorting_category=PlanSorting.by_activation,
            limit=1,
            offset=0,
        )
        response = self.query_plans_use_case(request)
        assert plan == response.results[0].plan_id
        return response.results[0].is_available
