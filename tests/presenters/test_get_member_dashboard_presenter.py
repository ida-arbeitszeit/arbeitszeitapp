from datetime import datetime
from decimal import Decimal
from typing import List
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_member_dashboard import GetMemberDashboard
from arbeitszeit_web.presenters.get_member_dashboard_presenter import (
    GetMemberDashboardPresenter,
)
from tests.presenters.url_index import PlanSummaryUrlIndexTestImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class GetMemberDashboardPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(GetMemberDashboardPresenter)
        self.plan_index = self.injector.get(PlanSummaryUrlIndexTestImpl)

    def test_that_welcome_line_is_correctly_translated(self) -> None:
        view_model = self.presenter.present(self.get_response())
        self.assertEqual(
            view_model.welcome_message,
            self.translator.gettext("Welcome, %s!") % self.get_response().name,
        )

    def test_that_workplaces_are_not_shown_when_worker_is_not_employed(self):
        presentation = self.presenter.present(self.get_response())
        self.assertFalse(presentation.show_workplaces)
        self.assertFalse(presentation.workplaces)

    def test_that_work_registration_info_is_shown_when_worker_is_not_employed(self):
        presentation = self.presenter.present(self.get_response())
        self.assertTrue(presentation.show_workplace_registration_info)

    def test_that_workplaces_are_shown_when_worker_is_employed(self):
        response = self.get_response(
            workplaces=[
                GetMemberDashboard.Workplace(
                    workplace_name="workplace_name", workplace_email="workplace@cp.org"
                ),
            ]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_workplaces)
        self.assertTrue(presentation.workplaces)

    def test_that_work_registration_info_is_not_shown_when_worker_is_employed(self):
        response = self.get_response(
            workplaces=[
                GetMemberDashboard.Workplace(
                    workplace_name="workplace_name", workplace_email="workplace@cp.org"
                ),
            ]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.show_workplace_registration_info)

    def test_that_account_balance_shows_only_two_digits_after_comma(self):
        response = self.get_response(account_balance=Decimal(1.3333333))
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.account_balance,
            self.translator.gettext("%.2f hours") % response.account_balance,
        )

    def test_that_latest_plans_is_empty_when_there_are_no_latest_plans(self):
        response = self.get_response(three_latest_plans=[])
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.three_latest_plans)

    def test_that_has_latest_plans_is_false_when_there_are_no_latest_plans(self):
        response = self.get_response(three_latest_plans=[])
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.has_latest_plans)

    def test_that_name_of_latest_plans_is_shown(self):
        expected_name = "test name"
        response = self.get_response(
            three_latest_plans=[
                GetMemberDashboard.PlanDetails(
                    plan_id=uuid4(),
                    prd_name=expected_name,
                    activation_date=datetime.now(),
                )
            ]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.three_latest_plans[0].prd_name, expected_name)

    def test_activation_date_of_latest_plans_is_correctly_formatted(self):
        now = datetime.now()
        response = self.get_response(
            three_latest_plans=[
                GetMemberDashboard.PlanDetails(
                    plan_id=uuid4(),
                    prd_name="test name",
                    activation_date=now,
                )
            ]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.three_latest_plans[0].activation_date, now.strftime("%d.%m.")
        )

    def test_plan_summary_url_is_correctly_shown(self):
        plan_id = uuid4()
        response = self.get_response(
            three_latest_plans=[
                GetMemberDashboard.PlanDetails(
                    plan_id=plan_id,
                    prd_name="test name",
                    activation_date=datetime.now(),
                )
            ]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.three_latest_plans[0].plan_summary_url,
            self.plan_index.get_plan_summary_url(plan_id),
        )

    def get_response(
        self,
        workplaces: List[GetMemberDashboard.Workplace] = None,
        account_balance: Decimal = None,
        three_latest_plans: List[GetMemberDashboard.PlanDetails] = None,
    ) -> GetMemberDashboard.Response:
        if workplaces is None:
            workplaces = []
        if account_balance is None:
            account_balance = Decimal(0)
        if three_latest_plans is None:
            three_latest_plans = []
        return GetMemberDashboard.Response(
            workplaces=workplaces,
            invites=[],
            three_latest_plans=three_latest_plans,
            account_balance=account_balance,
            name="worker",
            email="worker@cp.org",
            id=uuid4(),
        )
