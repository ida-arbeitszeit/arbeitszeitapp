from dataclasses import replace
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases.get_plan_summary_company import PlanSummaryCompanySuccess
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)

from .dependency_injection import get_dependency_injector
from .url_index import (
    EndCoopUrlIndexTestImpl,
    RequestCoopUrlIndexTestImpl,
    TogglePlanAvailabilityUrlIndex,
)

TESTING_RESPONSE_MODEL = PlanSummaryCompanySuccess(
    plan_summary=BusinessPlanSummary(
        plan_id=uuid4(),
        is_active=True,
        planner_id=uuid4(),
        planner_name="planner name",
        product_name="test product name",
        description="test description",
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
    ),
    current_user_is_planner=True,
)


class GetPlanSummaryCompanySuccessPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.toggle_availability_url_index = self.injector.get(
            TogglePlanAvailabilityUrlIndex
        )
        self.end_coop_url_index = self.injector.get(EndCoopUrlIndexTestImpl)
        self.request_coop_url_index = self.injector.get(RequestCoopUrlIndexTestImpl)
        self.presenter = self.injector.get(GetPlanSummaryCompanySuccessPresenter)

    def test_action_section_is_shown_when_current_user_is_planner(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.show_action_section)

    def test_action_section_is_not_shown_when_current_user_is_not_planner(self):
        response = replace(TESTING_RESPONSE_MODEL, current_user_is_planner=False)
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_action_section)

    def test_url_for_changing_availability_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.action.is_available,
            TESTING_RESPONSE_MODEL.plan_summary.is_available,
        )
        self.assertEqual(
            view_model.action.toggle_availability_url,
            self.toggle_availability_url_index.get_toggle_availability_url(
                TESTING_RESPONSE_MODEL.plan_summary.plan_id
            ),
        )

    def test_url_for_ending_cooperation_is_displayed_correctly_when_plan_is_cooperating(
        self,
    ):
        assert TESTING_RESPONSE_MODEL.plan_summary.cooperation
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.action.is_cooperating)
        self.assertEqual(
            view_model.action.end_coop_url,
            self.end_coop_url_index.get_end_coop_url(
                TESTING_RESPONSE_MODEL.plan_summary.plan_id,
                TESTING_RESPONSE_MODEL.plan_summary.cooperation,
            ),
        )

    def test_no_url_for_requesting_cooperation_is_displayed_when_plan_is_cooperating(
        self,
    ):
        assert TESTING_RESPONSE_MODEL.plan_summary.cooperation
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.action.is_cooperating)
        self.assertIsNone(view_model.action.request_coop_url)

    def test_no_url_for_ending_cooperation_is_displayed_when_plan_is_not_cooperating(
        self,
    ):
        plan_summary = replace(
            TESTING_RESPONSE_MODEL.plan_summary, is_cooperating=False, cooperation=None
        )
        response = PlanSummaryCompanySuccess(
            plan_summary=plan_summary, current_user_is_planner=True
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.action.is_cooperating)
        self.assertIsNone(view_model.action.end_coop_url)

    def test_url_for_requesting_cooperation_is_displayed_correctly_when_plan_is_not_cooperating(
        self,
    ):
        plan_summary = replace(
            TESTING_RESPONSE_MODEL.plan_summary, is_cooperating=False, cooperation=None
        )
        response = PlanSummaryCompanySuccess(
            plan_summary=plan_summary, current_user_is_planner=True
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.action.is_cooperating)
        self.assertEqual(
            view_model.action.request_coop_url,
            self.request_coop_url_index.get_request_coop_url(),
        )
