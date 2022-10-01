from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from arbeitszeit.use_cases.show_latest_plans import ShowLatestPlans
from arbeitszeit_web.presenters.show_latest_plans import ShowLatestPlansPresenter
from tests.datetime_service import FakeDatetimeService

from .base_test_case import BaseTestCase


class PresenterTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowLatestPlansPresenter)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_view_model_shows_that_there_are_no_plans_to_show(self) -> None:
        view_model = self.presenter.show_plans(self.get_empty_response())
        self.assertFalse(view_model.has_plans)

    def test_that_view_model_shows_that_there_are_plans_to_show(self) -> None:
        plan = self.get_latest_plan()
        response = self.get_response([plan])
        view_model = self.presenter.show_plans(response)
        self.assertTrue(view_model.has_plans)

    def test_that_view_model_shows_plans_activation_date_correctly_formatted(
        self,
    ) -> None:
        plan = self.get_latest_plan(activation_date=datetime(2022, 10, 1))
        response = self.get_response([plan])
        view_model = self.presenter.show_plans(response)
        self.assertEqual(view_model.plans[0].activation_date, "01.10.")

    def get_empty_response(self) -> ShowLatestPlans.Response:
        return ShowLatestPlans.Response([])

    def get_latest_plan(
        self,
        activation_date: datetime = None,
        plan_id: UUID = None,
        product_name: str = None,
    ) -> ShowLatestPlans.PlanDetail:
        if activation_date is None:
            activation_date = self.datetime_service.now_minus_one_day()
        if plan_id is None:
            plan_id = uuid4()
        if product_name is None:
            product_name = "product name"
        return ShowLatestPlans.PlanDetail(
            activation_date=activation_date, plan_id=plan_id, product_name=product_name
        )

    def get_response(
        self, plans: List[ShowLatestPlans.PlanDetail]
    ) -> ShowLatestPlans.Response:
        return ShowLatestPlans.Response(latest_plans=plans)
