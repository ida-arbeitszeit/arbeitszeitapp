from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import UUID

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases.show_my_plans import PlanInfo, ShowMyPlansResponse
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from tests.data_generators import PlanGenerator
from tests.use_cases.dependency_injection import get_dependency_injector


def _convert_into_plan_info(plan: Plan) -> PlanInfo:
    return PlanInfo(
        id=plan.id,
        prd_name=plan.prd_name,
        description=plan.description,
        price_per_unit=Decimal("10.001"),
        is_public_service=plan.is_public_service,
        plan_creation_date=plan.plan_creation_date,
        activation_date=plan.activation_date,
        expiration_date=plan.expiration_date,
        expiration_relative=plan.expiration_relative,
        is_available=plan.is_available,
        renewed=plan.renewed,
    )


def response_with_one_plan(plan: Plan) -> ShowMyPlansResponse:
    return ShowMyPlansResponse(
        count_all_plans=1,
        non_active_plans=[],
        active_plans=[],
        expired_plans=[],
    )


def response_with_one_active_plan(plan: Plan) -> ShowMyPlansResponse:
    plan_info = _convert_into_plan_info(plan)
    return ShowMyPlansResponse(
        count_all_plans=1,
        non_active_plans=[],
        active_plans=[plan_info],
        expired_plans=[],
    )


def response_with_one_expired_plan(plan: Plan) -> ShowMyPlansResponse:
    plan_info = _convert_into_plan_info(plan)
    return ShowMyPlansResponse(
        count_all_plans=1,
        non_active_plans=[],
        active_plans=[],
        expired_plans=[plan_info],
    )


def response_with_one_non_active_plan(plan: Plan) -> ShowMyPlansResponse:
    plan_info = _convert_into_plan_info(plan)
    return ShowMyPlansResponse(
        count_all_plans=1,
        non_active_plans=[plan_info],
        active_plans=[],
        expired_plans=[],
    )


class ShowMyPlansPresenterTests(TestCase):
    def setUp(self):
        self.url_index = PlanSummaryUrlIndex()
        self.presenter = ShowMyPlansPresenter(self.url_index)
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_show_notification_when_user_has_no_plans(self):
        presentation = self.presenter.present(
            ShowMyPlansResponse(
                count_all_plans=0,
                non_active_plans=[],
                active_plans=[],
                expired_plans=[],
            )
        )
        self.assertTrue(presentation.notifications)

    def test_do_not_show_notification_when_user_has_one_plan(self):
        plan = self.plan_generator.create_plan()
        RESPONSE_WITH_ONE_PLAN = response_with_one_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_PLAN)
        self.assertFalse(presentation.notifications)

    def test_do_only_show_active_plans_when_user_has_one_active_plan(self):
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        RESPONSE_WITH_ONE_ACTIVE_PLAN = response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ACTIVE_PLAN)
        self.assertTrue(presentation.show_active_plans)
        self.assertFalse(presentation.show_expired_plans)
        self.assertFalse(presentation.show_non_active_plans)

    def test_presenter_shows_correct_info_of_one_single_active_plan(self):
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        RESPONSE_WITH_ONE_ACTIVE_PLAN = response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ACTIVE_PLAN)
        self.assertEqual(presentation.active_plans.rows[0].id, str(plan.id))
        self.assertEqual(
            presentation.active_plans.rows[0].plan_summary_url,
            self.url_index.get_plan_summary_url(plan.id),
        )
        self.assertEqual(presentation.active_plans.rows[0].prd_name, plan.prd_name)
        self.assertEqual(
            presentation.active_plans.rows[0].description, plan.description.splitlines()
        )
        self.assertEqual(
            presentation.active_plans.rows[0].price_per_unit,
            str("10.00"),
        )
        self.assertEqual(
            presentation.active_plans.rows[0].type_of_plan,
            "Öffentlich" if plan.is_public_service else "Produktiv",
        )

    def test_presenter_shows_correct_plan_id_of_one_single_expired_plan(self):
        plan = self.plan_generator.create_plan(expired=True)
        RESPONSE_WITH_ONE_EXPIRED_PLAN = response_with_one_expired_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_EXPIRED_PLAN)
        self.assertEqual(presentation.expired_plans.rows[0].id, str(plan.id))

    def test_presenter_shows_correct_plan_id_of_one_single_non_active_plan(self):
        plan = self.plan_generator.create_plan(activation_date=None)
        RESPONSE_WITH_ONE_ON_ACTIVE_PLAN = response_with_one_non_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ON_ACTIVE_PLAN)
        self.assertEqual(presentation.non_active_plans.rows[0].id, str(plan.id))


class PlanSummaryUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return f"fake_plan_url:{plan_id}"
