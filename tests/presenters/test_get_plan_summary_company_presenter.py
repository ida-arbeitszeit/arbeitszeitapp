from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary_company import GetPlanSummaryCompany
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from tests.presenters.data_generators import PlanSummaryGenerator

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl

UseCaseResponse = GetPlanSummaryCompany.Response


class GetPlanSummaryCompanySuccessPresenterTests(TestCase):
    """
    some functionality are tested in tests/presenters/test_plan_summary_formatter.py
    """

    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.presenter = self.injector.get(GetPlanSummaryCompanySuccessPresenter)
        self.plan_summary_generator = self.injector.get(PlanSummaryGenerator)

    def test_action_section_is_shown_when_current_user_is_planner(self):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_own_plan_action_section)

    def test_action_section_is_not_shown_when_current_user_is_not_planner(self):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(),
            current_user_is_planner=False,
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_own_plan_action_section)

    def test_action_section_is_not_shown_when_current_user_is_planner_but_plan_is_expired(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_active=False
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_own_plan_action_section)

    def test_view_model_shows_availability_when_plan_is_available(self):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_available=True
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.own_plan_action.is_available_bool)

    def test_url_for_changing_availability_is_displayed_correctly(self):
        PLAN_ID = uuid4()
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                plan_id=PLAN_ID
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.own_plan_action.toggle_availability_url,
            self.url_index.get_toggle_availability_url(PLAN_ID),
        )

    def test_view_model_shows_plan_as_cooperating_when_plan_is_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=True
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.own_plan_action.is_cooperating)

    def test_url_for_ending_cooperation_is_displayed_correctly_when_plan_is_cooperating(
        self,
    ):
        PLAN_ID = uuid4()
        COOPERATION = uuid4()
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=True, plan_id=PLAN_ID, cooperation=COOPERATION
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.own_plan_action.end_coop_url,
            self.url_index.get_end_coop_url(
                plan_id=PLAN_ID,
                cooperation_id=COOPERATION,
            ),
        )

    def test_no_url_for_requesting_cooperation_is_displayed_when_plan_is_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=True
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.own_plan_action.request_coop_url)

    def test_no_url_for_ending_cooperation_is_displayed_when_plan_is_not_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=False, cooperation=None
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.own_plan_action.end_coop_url)

    def test_url_for_requesting_cooperation_is_displayed_correctly_when_plan_is_not_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=False, cooperation=None
            ),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.own_plan_action.is_cooperating)
        self.assertEqual(
            view_model.own_plan_action.request_coop_url,
            self.url_index.get_request_coop_url(),
        )

    def test_url_for_paying_product_is_displayed_when_user_is_not_planner_of_plan(
        self,
    ):
        response = UseCaseResponse(
            self.plan_summary_generator.create_plan_summary(),
            current_user_is_planner=False,
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_payment_url)

    def test_correct_url_for_paying_product_is_displayed(
        self,
    ):
        PLAN_ID = uuid4()
        response = UseCaseResponse(
            self.plan_summary_generator.create_plan_summary(plan_id=PLAN_ID),
            current_user_is_planner=False,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.payment_url,
            self.url_index.get_pay_means_of_production_url(PLAN_ID),
        )

    def test_url_for_paying_product_is_not_displayed_when_user_is_planner_of_plan(
        self,
    ):
        response = UseCaseResponse(
            self.plan_summary_generator.create_plan_summary(),
            current_user_is_planner=True,
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_payment_url)
