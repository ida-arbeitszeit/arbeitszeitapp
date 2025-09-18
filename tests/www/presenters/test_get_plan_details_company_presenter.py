"""
some functionalities are tested in tests/presenters/test_plan_details_formatter.py
"""

from uuid import uuid4

from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit_web.www.presenters.get_plan_details_company_presenter import (
    GetPlanDetailsCompanyPresenter,
)
from tests.www.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import PlanDetailsGenerator

InteractorResponse = GetPlanDetailsInteractor.Response


class TestPresenterForPlanner(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanDetailsCompanyPresenter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)
        self.expected_planner = uuid4()
        self.session.login_company(company=self.expected_planner)

    def test_action_section_is_shown_when_current_user_is_planner(self):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_own_plan_action_section)

    def test_action_section_is_not_shown_when_current_user_is_planner_but_plan_is_expired(
        self,
    ):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                is_active=False, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_own_plan_action_section)

    def test_plan_id_is_displayed_correctly(self):
        expected_plan_id = uuid4()
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                plan_id=expected_plan_id, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        assert view_model.own_plan_action.plan_id == str(expected_plan_id)

    def test_cooperation_id_is_displayed_correctly_when_plan_is_cooperating(
        self,
    ):
        expected_cooperation_id = uuid4()
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                is_cooperating=True,
                plan_id=uuid4(),
                cooperation=expected_cooperation_id,
                planner_id=self.expected_planner,
            ),
        )
        view_model = self.presenter.present(response)
        assert view_model.own_plan_action.cooperation_id == str(expected_cooperation_id)

    def test_cooperation_id_is_none_when_plan_is_not_cooperating(self):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                is_cooperating=False, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        assert not view_model.own_plan_action.cooperation_id

    def test_no_url_for_requesting_cooperation_is_displayed_when_plan_is_cooperating(
        self,
    ):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                is_cooperating=True, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.own_plan_action.request_coop_url)

    def test_url_for_requesting_cooperation_is_displayed_correctly_when_plan_is_not_cooperating(
        self,
    ):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                is_cooperating=False, cooperation=None, planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.own_plan_action.is_cooperating)
        self.assertEqual(
            view_model.own_plan_action.request_coop_url,
            self.url_index.get_request_coop_url(),
        )

    def test_url_for_consuming_product_is_not_displayed_when_user_is_planner_of_plan(
        self,
    ):
        response = InteractorResponse(
            self.plan_details_generator.create_plan_details(
                planner_id=self.expected_planner
            ),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_productive_consumption_url)


class TestPresenterForNonPlanningCompany(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanDetailsCompanyPresenter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)
        self.session.login_company(uuid4())

    def test_action_section_is_not_shown_when_current_user_is_not_planner(self):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(),
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_own_plan_action_section)

    def test_view_model_shows_plan_as_cooperating_when_plan_is_cooperating(
        self,
    ):
        response = InteractorResponse(
            plan_details=self.plan_details_generator.create_plan_details(
                is_cooperating=True
            ),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.own_plan_action.is_cooperating)

    def test_url_for_consuming_product_is_displayed_when_user_is_not_planner_of_plan(
        self,
    ):
        response = InteractorResponse(
            self.plan_details_generator.create_plan_details(),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_productive_consumption_url)

    def test_correct_url_for_consuming_product_is_displayed(
        self,
    ):
        expected_plan_id = uuid4()
        response = InteractorResponse(
            self.plan_details_generator.create_plan_details(plan_id=expected_plan_id),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.productive_consumption_url,
            self.url_index.get_register_productive_consumption_url(expected_plan_id),
        )
