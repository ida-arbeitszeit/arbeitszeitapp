from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases.show_my_plans import PlanInfo, ShowMyPlansResponse
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import (
    HidePlanUrlIndexTestImpl,
    RenewPlanUrlIndexTestImpl,
    UrlIndexTestImpl,
)


class ShowMyPlansPresenterTests(TestCase):
    def setUp(self):
        self.injector = get_dependency_injector()
        self.plan_url_index = self.injector.get(UrlIndexTestImpl)
        self.renew_plan_url_index = self.injector.get(RenewPlanUrlIndexTestImpl)
        self.hide_plan_url_index = self.injector.get(HidePlanUrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(ShowMyPlansPresenter)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.update_plans_use_case = self.injector.get(UpdatePlansAndPayout)
        self.session = self.injector.get(FakeSession)
        self.session.login_company("test@test.test")

    def test_show_correct_notification_when_user_has_no_plans(self):
        presentation = self.presenter.present(
            ShowMyPlansResponse(
                count_all_plans=0,
                non_active_plans=[],
                active_plans=[],
                expired_plans=[],
                drafts=[],
            )
        )
        self.assertTrue(presentation.notifications)
        self.assertEqual(
            presentation.notifications,
            [self.translator.gettext("You don't have any plans.")],
        )

    def test_do_not_show_notification_when_user_has_one_plan(self):
        plan = self.plan_generator.create_plan()
        RESPONSE_WITH_ONE_PLAN = self.response_with_one_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_PLAN)
        self.assertFalse(presentation.notifications)

    def test_do_only_show_active_plans_when_user_has_one_active_plan(self):
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        RESPONSE_WITH_ONE_ACTIVE_PLAN = self.response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ACTIVE_PLAN)
        self.assertTrue(presentation.show_active_plans)
        self.assertFalse(presentation.show_expired_plans)
        self.assertFalse(presentation.show_non_active_plans)

    def test_presenter_shows_correct_info_of_one_single_active_plan(self):
        plan = self.plan_generator.create_plan(
            activation_date=datetime.min, cooperation=None, is_available=True
        )
        RESPONSE_WITH_ONE_ACTIVE_PLAN = self.response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ACTIVE_PLAN)
        self.assertEqual(
            presentation.active_plans.rows[0].plan_summary_url,
            self.plan_url_index.get_plan_summary_url(UserRole.company, plan.id),
        )
        self.assertEqual(presentation.active_plans.rows[0].prd_name, plan.prd_name)
        self.assertEqual(
            presentation.active_plans.rows[0].price_per_unit,
            str("10.00"),
        )
        self.assertEqual(
            presentation.active_plans.rows[0].is_public_service, plan.is_public_service
        )
        self.assertEqual(
            presentation.active_plans.rows[0].is_available,
            True,
        )
        self.assertEqual(
            presentation.active_plans.rows[0].is_cooperating,
            False,
        )

    def test_presenter_shows_correct_info_of_one_single_plan_that_is_cooperating(self):
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        coop = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            activation_date=datetime(2000, 1, 1), cooperation=coop, is_available=True
        )
        RESPONSE_WITH_COOPERATING_PLAN = self.response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_COOPERATING_PLAN)
        self.assertEqual(
            presentation.active_plans.rows[0].is_cooperating,
            True,
        )

    def test_presenter_shows_correct_info_of_one_single_expired_plan(self):
        plan = self.plan_generator.create_plan()
        plan.expired = True
        RESPONSE_WITH_ONE_EXPIRED_PLAN = self.response_with_one_expired_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_EXPIRED_PLAN)
        row1 = presentation.expired_plans.rows[0]
        expected_plan = RESPONSE_WITH_ONE_EXPIRED_PLAN.expired_plans[0]
        self.assertEqual(
            row1.plan_summary_url,
            self.plan_url_index.get_plan_summary_url(UserRole.company, plan.id),
        )
        self.assertEqual(
            row1.prd_name,
            expected_plan.prd_name,
        )
        self.assertEqual(row1.is_public_service, plan.is_public_service)
        self.assertEqual(
            row1.renew_plan_url, self.renew_plan_url_index.get_renew_plan_url(plan.id)
        )
        self.assertEqual(
            row1.hide_plan_url, self.hide_plan_url_index.get_hide_plan_url(plan.id)
        )

    def test_presenter_shows_correct_info_of_one_single_non_active_plan(self) -> None:
        plan = self.plan_generator.create_plan(activation_date=None)
        RESPONSE_WITH_ONE_NON_ACTIVE_PLAN = self.response_with_one_non_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_NON_ACTIVE_PLAN)
        row1 = presentation.non_active_plans.rows[0]
        expected_plan = RESPONSE_WITH_ONE_NON_ACTIVE_PLAN.non_active_plans[0]
        self.assertEqual(
            row1.plan_summary_url,
            self.plan_url_index.get_plan_summary_url(UserRole.company, plan.id),
        )
        self.assertEqual(
            row1.prd_name,
            expected_plan.prd_name,
        )
        self.assertEqual(
            row1.price_per_unit,
            format_price(expected_plan.price_per_unit),
        )
        self.assertEqual(row1.type_of_plan, self.translator.gettext("Productive"))

    def test_that_relative_expiration_is_calculated_correctly(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self._create_active_plan(timeframe=5)
        view_model = self.presenter.present(self.response_with_one_active_plan(plan))
        self.assertEqual(
            view_model.active_plans.rows[0].expiration_relative,
            "5",
        )

    def _convert_into_plan_info(self, plan: Plan) -> PlanInfo:
        return PlanInfo(
            id=plan.id,
            prd_name=plan.prd_name,
            price_per_unit=Decimal("10.001"),
            is_public_service=plan.is_public_service,
            plan_creation_date=plan.plan_creation_date,
            activation_date=plan.activation_date,
            expiration_date=plan.expiration_date,
            is_available=plan.is_available,
            is_cooperating=bool(plan.cooperation),
            cooperation=plan.cooperation,
        )

    def response_with_one_plan(self, plan: Plan) -> ShowMyPlansResponse:
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[],
            active_plans=[],
            expired_plans=[],
            drafts=[],
        )

    def response_with_one_active_plan(self, plan: Plan) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[],
            active_plans=[plan_info],
            expired_plans=[],
            drafts=[],
        )

    def response_with_one_expired_plan(self, plan: Plan) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[],
            active_plans=[],
            expired_plans=[plan_info],
            drafts=[],
        )

    def response_with_one_non_active_plan(self, plan: Plan) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[plan_info],
            active_plans=[],
            expired_plans=[],
            drafts=[],
        )

    def _create_active_plan(self, timeframe: int = 1) -> Plan:
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
            timeframe=timeframe,
        )
        self.update_plans_use_case()
        return plan


def format_price(price_per_unit: Decimal) -> str:
    return f"{round(price_per_unit, 2)}"
