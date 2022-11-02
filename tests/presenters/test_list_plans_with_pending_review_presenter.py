from uuid import uuid4

from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase as UseCase,
)
from arbeitszeit_web.presenters.list_plans_with_pending_review_presenter import (
    ListPlansWithPendingReviewPresenter,
)

from .base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListPlansWithPendingReviewPresenter)

    def test_that_plan_overview_is_not_shown_when_there_are_no_plans_in_response(
        self,
    ) -> None:
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_empty_response()
        )
        self.assertFalse(view_model.show_plan_list)

    def test_that_plan_overview_is_shown_when_there_is_one_plan_in_response(
        self,
    ) -> None:
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan()
        )
        self.assertTrue(view_model.show_plan_list)

    def test_that_product_name_is_listed_correctly_with_one_plan(self) -> None:
        expected_product_name = "test product name"
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(product_name=expected_product_name)
        )
        self.assertEqual(view_model.plans[0].product_name, expected_product_name)

    def test_that_planner_name_is_listed_correctly_with_one_plan(self) -> None:
        expected_planner_name = "test planner name 123"
        view_model = self.presenter.list_plans_with_pending_review(
            self._get_response_with_one_plan(planner_name=expected_planner_name)
        )
        self.assertEqual(view_model.plans[0].planner_name, expected_planner_name)

    def _get_empty_response(self) -> UseCase.Response:
        return UseCase.Response(plans=[])

    def _get_response_with_one_plan(
        self,
        *,
        product_name: str = "test product",
        planner_name: str = "example company",
    ) -> UseCase.Response:
        return UseCase.Response(
            plans=[
                UseCase.Plan(
                    id=uuid4(), product_name=product_name, planner_name=planner_name
                )
            ]
        )
