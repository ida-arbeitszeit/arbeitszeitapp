from dataclasses import replace
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases.get_plan_summary_company import PlanSummaryCompanySuccess
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from tests.plan_summary import FakePlanSummaryService
from tests.translator import FakeTranslator

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
        self.coop_url_index = CoopSummaryUrlIndex()
        self.toggle_availability_url_index = TogglePlanAvailabilityUrlIndex()
        self.end_coop_url_index = EndCoopUrlIndex()
        self.translator = FakeTranslator()
        self.plan_summary_service = FakePlanSummaryService()
        self.presenter = GetPlanSummaryCompanySuccessPresenter(
            self.toggle_availability_url_index,
            self.end_coop_url_index,
            self.translator,
            self.plan_summary_service,
        )

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
        self.assertEqual(
            view_model.action.is_cooperating,
            TESTING_RESPONSE_MODEL.plan_summary.is_cooperating,
        )
        self.assertEqual(
            view_model.action.end_coop_url,
            self.end_coop_url_index.get_end_coop_url(
                TESTING_RESPONSE_MODEL.plan_summary.plan_id,
                TESTING_RESPONSE_MODEL.plan_summary.cooperation,
            ),
        )

    def test_url_for_ending_cooperation_is_displayed_correctly_when_plan_is_not_cooperating(
        self,
    ):
        plan_summary = replace(
            TESTING_RESPONSE_MODEL.plan_summary, is_cooperating=False, cooperation=None
        )
        response = PlanSummaryCompanySuccess(
            plan_summary=plan_summary, current_user_is_planner=True
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.action.is_cooperating, response.plan_summary.is_cooperating
        )
        self.assertEqual(view_model.action.end_coop_url, None)


class CoopSummaryUrlIndex:
    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return f"fake_coop_url:{coop_id}"


class TogglePlanAvailabilityUrlIndex:
    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        return f"fake_toggle_url:{plan_id}"


class EndCoopUrlIndex:
    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return f"fake_end_coop_url:{plan_id}, {cooperation_id}"
