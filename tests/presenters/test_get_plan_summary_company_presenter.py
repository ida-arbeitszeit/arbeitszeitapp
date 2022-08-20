from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases.get_plan_summary_company import GetPlanSummaryCompany
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl

TESTING_PLAN_SUMMARY = PlanSummary(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
    planner_name="planner name",
    product_name="test product name",
    description="test description",
    active_days=5,
    timeframe=7,
    production_unit="Piece",
    amount=100,
    means_cost=Decimal(1),
    resources_cost=Decimal(2),
    labour_cost=Decimal(3),
    is_public_service=False,
    price_per_unit=Decimal("0.061"),
    is_available=True,
    is_cooperating=True,
    cooperation=uuid4(),
    creation_date=datetime.now(),
    approval_date=None,
    expiration_date=None,
)

TESTING_RESPONSE_MODEL = GetPlanSummaryCompany.Response(
    plan_summary=TESTING_PLAN_SUMMARY,
    current_user_is_planner=True,
)


class GetPlanSummaryCompanySuccessPresenterTests(TestCase):
    """
    some functionality are tested in tests/presenters/test_plan_summary_service.py
    """

    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.presenter = self.injector.get(GetPlanSummaryCompanySuccessPresenter)

    def test_action_section_is_shown_when_current_user_is_planner(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.show_action_section)

    def test_action_section_is_not_shown_when_current_user_is_not_planner(self):
        response = replace(TESTING_RESPONSE_MODEL, current_user_is_planner=False)
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_action_section)

    def test_view_model_sows_availability_when_plan_is_available(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.action.is_available_bool,
            TESTING_PLAN_SUMMARY.is_available,
        )

    def test_url_for_changing_availability_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.action.toggle_availability_url,
            self.url_index.get_toggle_availability_url(TESTING_PLAN_SUMMARY.plan_id),
        )

    def test_view_model_shows_plan_as_cooperating_when_plan_is_cooperating(
        self,
    ):
        assert TESTING_PLAN_SUMMARY.cooperation
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.action.is_cooperating)
        self.assertEqual(
            view_model.action.is_cooperating,
            TESTING_PLAN_SUMMARY.is_cooperating,
        )

    def test_url_for_ending_cooperation_is_displayed_correctly_when_plan_is_cooperating(
        self,
    ):
        assert TESTING_PLAN_SUMMARY.cooperation
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.action.is_cooperating)
        self.assertEqual(
            view_model.action.end_coop_url,
            self.url_index.get_end_coop_url(
                TESTING_PLAN_SUMMARY.plan_id,
                TESTING_PLAN_SUMMARY.cooperation,
            ),
        )

    def test_no_url_for_requesting_cooperation_is_displayed_when_plan_is_cooperating(
        self,
    ):
        assert TESTING_PLAN_SUMMARY.cooperation
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.action.is_cooperating)
        self.assertIsNone(view_model.action.request_coop_url)

    def test_no_url_for_ending_cooperation_is_displayed_when_plan_is_not_cooperating(
        self,
    ):
        plan_summary = replace(
            TESTING_PLAN_SUMMARY, is_cooperating=False, cooperation=None
        )
        response = GetPlanSummaryCompany.Response(
            plan_summary=plan_summary, current_user_is_planner=True
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.action.is_cooperating)
        self.assertIsNone(view_model.action.end_coop_url)

    def test_url_for_requesting_cooperation_is_displayed_correctly_when_plan_is_not_cooperating(
        self,
    ):
        plan_summary = replace(
            TESTING_PLAN_SUMMARY, is_cooperating=False, cooperation=None
        )
        response = GetPlanSummaryCompany.Response(
            plan_summary=plan_summary, current_user_is_planner=True
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.action.is_cooperating)
        self.assertEqual(
            view_model.action.request_coop_url,
            self.url_index.get_request_coop_url(),
        )

    def test_url_for_paying_product_is_displayed_when_user_is_not_planner_of_plan(
        self,
    ):
        response = replace(TESTING_RESPONSE_MODEL, current_user_is_planner=False)
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_payment_url)

    def test_correct_url_for_paying_product_is_displayed(
        self,
    ):
        response = replace(TESTING_RESPONSE_MODEL, current_user_is_planner=False)
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.payment_url,
            self.url_index.get_pay_means_of_production_with_plan_parameter_url(
                TESTING_PLAN_SUMMARY.plan_id
            ),
        )

    def test_url_for_paying_product_is_not_displayed_when_user_is_planner_of_plan(
        self,
    ):
        assert TESTING_RESPONSE_MODEL.current_user_is_planner
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertFalse(view_model.show_payment_url)
