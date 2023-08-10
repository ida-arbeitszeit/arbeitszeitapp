from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.start_page import StartPageUseCase
from arbeitszeit_web.www.presenters.start_page_presenter import StartPagePresenter
from tests.www.base_test_case import BaseTestCase


class PresenterTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(StartPagePresenter)

    def test_that_view_model_shows_that_there_are_no_plans_to_show(self) -> None:
        view_model = self.presenter.show_start_page(self.get_empty_response())
        self.assertFalse(view_model.show_plans)

    def test_that_view_model_shows_that_there_are_plans_to_show(self) -> None:
        plan = self.get_latest_plan()
        response = self.get_response([plan])
        view_model = self.presenter.show_start_page(response)
        self.assertTrue(view_model.show_plans)

    def test_that_view_model_shows_plans_activation_date_correctly_formatted(
        self,
    ) -> None:
        plan = self.get_latest_plan(activation_date=datetime(2022, 10, 1))
        response = self.get_response([plan])
        view_model = self.presenter.show_start_page(response)
        self.assertEqual(view_model.plans[0].activation_date, "01.10.")

    def get_empty_response(self) -> StartPageUseCase.Response:
        return StartPageUseCase.Response([])

    def get_latest_plan(
        self,
        activation_date: Optional[datetime] = None,
        plan_id: Optional[UUID] = None,
        product_name: Optional[str] = None,
    ) -> StartPageUseCase.PlanDetail:
        if activation_date is None:
            activation_date = datetime(2022, 5, 1)
        if plan_id is None:
            plan_id = uuid4()
        if product_name is None:
            product_name = "product name"
        return StartPageUseCase.PlanDetail(
            activation_date=activation_date, plan_id=plan_id, product_name=product_name
        )

    def get_response(
        self, plans: List[StartPageUseCase.PlanDetail]
    ) -> StartPageUseCase.Response:
        return StartPageUseCase.Response(latest_plans=plans)
