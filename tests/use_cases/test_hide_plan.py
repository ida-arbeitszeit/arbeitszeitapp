from uuid import UUID

from arbeitszeit.use_cases.hide_plan import HidePlanUseCase
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.hide_plan = self.injector.get(HidePlanUseCase)
        self.show_my_plans_use_case = self.injector.get(ShowMyPlansUseCase)
        self.now = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(self.now)

    def test_that_correct_plan_gets_hidden_attribute_set_to_true(self) -> None:
        planner = self.company_generator.create_company()
        plan1 = self.create_expired_plan(planner)
        plan2 = self.create_expired_plan(planner)
        plan3 = self.create_expired_plan(planner)
        self.hide_plan.execute(plan2)
        assert not self.is_plan_hidden(plan=plan1, planner=planner)
        assert self.is_plan_hidden(plan=plan2, planner=planner)
        assert not self.is_plan_hidden(plan=plan3, planner=planner)

    def test_that_correct_response_gets_returned(self) -> None:
        plan = self.create_expired_plan()
        response = self.hide_plan.execute(plan)
        self.assertEqual(response.plan_id, plan)
        self.assertEqual(response.is_success, True)

    def test_that_active_plans_do_not_get_hidden_and_correct_response_gets_returned(
        self,
    ) -> None:
        plan = self.create_active_plan()
        response = self.hide_plan.execute(plan)
        assert response.plan_id == plan
        assert response.is_success == False

    def create_expired_plan(self, planner: UUID | None = None) -> UUID:
        if not planner:
            planner = self.company_generator.create_company()
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.plan_generator.create_plan(planner=planner, timeframe=1)
        self.datetime_service.unfreeze_time()
        return plan

    def create_active_plan(self) -> UUID:
        return self.plan_generator.create_plan()

    def is_plan_hidden(self, *, plan: UUID, planner: UUID) -> bool:
        request = ShowMyPlansRequest(planner)
        response = self.show_my_plans_use_case.show_company_plans(request)
        return plan not in (
            plan_info.id
            for plan_info in (
                response.non_active_plans
                + response.active_plans
                + response.expired_plans
            )
        )
