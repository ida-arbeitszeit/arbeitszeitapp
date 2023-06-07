"""
some functionalities are tested in tests/presenters/test_plan_summary_formatter.py
"""

from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from arbeitszeit_web.get_plan_summary_company import GetPlanSummaryCompanyPresenter
from tests.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import PlanSummaryGenerator
from tests.session import FakeSession

from .url_index import UrlIndexTestImpl

UseCaseResponse = GetPlanSummaryUseCase.Response


class TestPresenterForPlanner(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.presenter = self.injector.get(GetPlanSummaryCompanyPresenter)
        self.plan_summary_generator = self.injector.get(PlanSummaryGenerator)
        self.session = self.injector.get(FakeSession)
        self.expected_planner = uuid4()
        self.session.login_company(company=self.expected_planner)

    def test_action_section_is_shown_when_current_user_is_planner(self):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_own_plan_action_section)

    def test_action_section_is_not_shown_when_current_user_is_planner_but_plan_is_expired(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_active=False, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_own_plan_action_section)

    def test_url_for_changing_availability_is_displayed_correctly(self):
        expected_plan_id = uuid4()
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                plan_id=expected_plan_id, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.own_plan_action.toggle_availability_url,
            self.url_index.get_toggle_availability_url(expected_plan_id),
        )

    def test_url_for_ending_cooperation_is_displayed_correctly_when_plan_is_cooperating(
        self,
    ):
        expected_plan_id = uuid4()
        expected_cooperation_id = uuid4()
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=True,
                plan_id=expected_plan_id,
                cooperation=expected_cooperation_id,
                planner_id=self.expected_planner,
            ),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.own_plan_action.end_coop_url,
            self.url_index.get_end_coop_url(
                plan_id=expected_plan_id,
                cooperation_id=expected_cooperation_id,
            ),
        )

    def test_no_url_for_requesting_cooperation_is_displayed_when_plan_is_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=True, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.own_plan_action.request_coop_url)

    def test_no_url_for_ending_cooperation_is_displayed_when_plan_is_not_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=False, cooperation=None, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.own_plan_action.end_coop_url)

    def test_url_for_requesting_cooperation_is_displayed_correctly_when_plan_is_not_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=False, cooperation=None, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.own_plan_action.is_cooperating)
        self.assertEqual(
            view_model.own_plan_action.request_coop_url,
            self.url_index.get_request_coop_url(),
        )

    def test_url_for_paying_product_is_not_displayed_when_user_is_planner_of_plan(
        self,
    ):
        response = UseCaseResponse(
            self.plan_summary_generator.create_plan_summary(
                planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_payment_url)


class TestPresenterForNonPlanningCompany(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.presenter = self.injector.get(GetPlanSummaryCompanyPresenter)
        self.plan_summary_generator = self.injector.get(PlanSummaryGenerator)
        self.session = self.injector.get(FakeSession)
        self.session.login_company(uuid4())

    def test_action_section_is_not_shown_when_current_user_is_not_planner(self):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_own_plan_action_section)

    def test_view_model_shows_availability_when_plan_is_available(self):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_available=True
            ),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.own_plan_action.is_available_bool)

    def test_view_model_shows_plan_as_cooperating_when_plan_is_cooperating(
        self,
    ):
        response = UseCaseResponse(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                is_cooperating=True
            ),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.own_plan_action.is_cooperating)

    def test_url_for_paying_product_is_displayed_when_user_is_not_planner_of_plan(
        self,
    ):
        response = UseCaseResponse(
            self.plan_summary_generator.create_plan_summary(),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_payment_url)

    def test_correct_url_for_paying_product_is_displayed(
        self,
    ):
        expected_plan_id = uuid4()
        response = UseCaseResponse(
            self.plan_summary_generator.create_plan_summary(plan_id=expected_plan_id),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.payment_url,
            self.url_index.get_pay_means_of_production_url(expected_plan_id),
        )
