from datetime import datetime
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_latest_activated_plans import GetLatestActivatedPlans
from arbeitszeit_web.presenters.get_latest_activated_plans_presenter import (
    GetLatestActivatedPlansPresenter,
)
from tests.presenters.dependency_injection import get_dependency_injector
from tests.presenters.url_index import PlanSummaryUrlIndexTestImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_index = self.injector.get(PlanSummaryUrlIndexTestImpl)
        self.presenter = self.injector.get(GetLatestActivatedPlansPresenter)
        self.default_response_with_one_plan = GetLatestActivatedPlans.Response(
            plans=[
                GetLatestActivatedPlans.PlanDetail(
                    plan_id=uuid4(),
                    prd_name="prd name",
                    activation_date=datetime(2022, 5, 16),
                )
            ]
        )
        self.default_response_with_two_plans = GetLatestActivatedPlans.Response(
            plans=[
                GetLatestActivatedPlans.PlanDetail(
                    plan_id=uuid4(),
                    prd_name="prd name",
                    activation_date=datetime(2022, 5, 16),
                ),
                GetLatestActivatedPlans.PlanDetail(
                    plan_id=uuid4(),
                    prd_name="prd name2",
                    activation_date=datetime(2022, 5, 17),
                ),
            ]
        )

    def test_nothing_shown_when_use_case_response_is_empty(self):
        view_model = self.presenter.show_latest_plans(
            GetLatestActivatedPlans.Response(plans=[])
        )
        self.assertFalse(view_model.latest_plans)
        self.assertFalse(view_model.has_latest_plans)

    def test_one_plan_is_shown_when_use_case_response_has_one_plan(self):
        view_model = self.presenter.show_latest_plans(
            self.default_response_with_one_plan
        )
        self.assertEqual(view_model.latest_plans.__len__(), 1)
        self.assertTrue(view_model.has_latest_plans)

    def test_two_plans_are_shown_when_use_case_response_has_two_plans(self):
        view_model = self.presenter.show_latest_plans(
            self.default_response_with_two_plans
        )
        self.assertEqual(view_model.latest_plans.__len__(), 2)

    def test_prd_name_is_correctly_shown(self):
        view_model = self.presenter.show_latest_plans(
            self.default_response_with_one_plan
        )
        self.assertEqual(
            view_model.latest_plans[0].prd_name,
            self.default_response_with_one_plan.plans[0].prd_name,
        )

    def test_activation_date_is_correctly_shown(self):
        view_model = self.presenter.show_latest_plans(
            self.default_response_with_one_plan
        )
        self.assertEqual(
            view_model.latest_plans[0].activation_date,
            str(self.default_response_with_one_plan.plans[0].activation_date),
        )

    def test_plan_summary_url_is_correctly_shown(self):
        view_model = self.presenter.show_latest_plans(
            self.default_response_with_one_plan
        )
        self.assertEqual(
            view_model.latest_plans[0].plan_summary_url,
            self.plan_index.get_plan_summary_url(
                self.default_response_with_one_plan.plans[0].plan_id
            ),
        )
