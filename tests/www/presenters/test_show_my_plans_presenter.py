from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.records import Plan, PlanDraft
from arbeitszeit.use_cases.show_my_plans import (
    PlanInfo,
    ShowMyPlansRequest,
    ShowMyPlansResponse,
    ShowMyPlansUseCase,
)
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.show_my_plans_presenter import ShowMyPlansPresenter
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.www.base_test_case import BaseTestCase


class ShowMyPlansPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyPlansPresenter)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.session.login_company(uuid4())
        self.show_my_plans = self.injector.get(ShowMyPlansUseCase)
        self.datetime_service.freeze_time(datetime(2000, 1, 1))

    def test_show_correct_notification_when_user_has_no_plans(self) -> None:
        self.presenter.present(
            ShowMyPlansResponse(
                count_all_plans=0,
                non_active_plans=[],
                active_plans=[],
                expired_plans=[],
                drafts=[],
                rejected_plans=[],
            )
        )
        self.assertTrue(self.notifier.display_info)
        self.assertEqual(
            self.notifier.infos,
            [self.translator.gettext("You don't have any plans.")],
        )

    def test_do_not_show_notification_when_user_has_one_plan(self) -> None:
        plan = self.plan_generator.create_plan_record()
        RESPONSE_WITH_ONE_PLAN = self.response_with_one_plan(plan)
        self.presenter.present(RESPONSE_WITH_ONE_PLAN)
        self.assertFalse(self.notifier.infos)
        self.assertFalse(self.notifier.warnings)

    def test_do_only_show_active_plans_when_user_has_one_active_plan(self) -> None:
        plan = self.plan_generator.create_plan_record()
        RESPONSE_WITH_ONE_ACTIVE_PLAN = self.response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ACTIVE_PLAN)
        self.assertTrue(presentation.show_active_plans)
        self.assertFalse(presentation.show_expired_plans)
        self.assertFalse(presentation.show_non_active_plans)
        self.assertFalse(presentation.show_rejected_plans)

    def test_presenter_shows_correct_info_of_one_single_active_plan(self) -> None:
        plan = self.plan_generator.create_plan_record(cooperation=None)
        RESPONSE_WITH_ONE_ACTIVE_PLAN = self.response_with_one_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_ACTIVE_PLAN)
        self.assertEqual(
            presentation.active_plans.rows[0].plan_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan.id
            ),
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
            presentation.active_plans.rows[0].is_cooperating,
            False,
        )

    def test_presenter_shows_correct_info_of_one_single_plan_that_is_cooperating(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        coop = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan_record(cooperation=coop)
        RESPONSE_WITH_COOPERATING_PLAN = self.response_with_one_active_plan(
            plan, cooperation=coop
        )
        presentation = self.presenter.present(RESPONSE_WITH_COOPERATING_PLAN)
        self.assertEqual(
            presentation.active_plans.rows[0].is_cooperating,
            True,
        )

    def test_presenter_shows_correct_info_of_one_single_expired_plan(self) -> None:
        RESPONSE_WITH_ONE_EXPIRED_PLAN = self.response_with_one_expired_plan()
        presentation = self.presenter.present(RESPONSE_WITH_ONE_EXPIRED_PLAN)
        row1 = presentation.expired_plans.rows[0]
        expected_plan = RESPONSE_WITH_ONE_EXPIRED_PLAN.expired_plans[0]
        self.assertEqual(
            row1.plan_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=expected_plan.id
            ),
        )
        self.assertEqual(
            row1.prd_name,
            expected_plan.prd_name,
        )
        self.assertEqual(row1.is_public_service, expected_plan.is_public_service)
        self.assertEqual(
            row1.renew_plan_url,
            self.url_index.get_renew_plan_url(expected_plan.id),
        )
        self.assertEqual(
            row1.hide_plan_url,
            self.url_index.get_hide_plan_url(expected_plan.id),
        )

    def test_presenter_shows_correct_info_of_one_single_non_active_plan(self) -> None:
        plan = self.plan_generator.create_plan_record(approved=False)
        RESPONSE_WITH_ONE_NON_ACTIVE_PLAN = self.response_with_one_non_active_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_NON_ACTIVE_PLAN)
        row1 = presentation.non_active_plans.rows[0]
        expected_plan = RESPONSE_WITH_ONE_NON_ACTIVE_PLAN.non_active_plans[0]
        self.assertEqual(
            row1.plan_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan.id
            ),
        )
        self.assertEqual(
            row1.prd_name,
            expected_plan.prd_name,
        )
        self.assertEqual(
            row1.price_per_unit,
            "10.00",
        )
        self.assertEqual(row1.type_of_plan, self.translator.gettext("Productive"))

    def test_non_active_plan_has_correct_revocation_url(self) -> None:
        plan = self.plan_generator.create_plan_record(approved=False)
        use_case_response = self.response_with_one_non_active_plan(plan)
        view_model = self.presenter.present(use_case_response)
        row = view_model.non_active_plans.rows[0]
        self.assertEqual(
            row.revoke_plan_filing_url,
            self.url_index.get_revoke_plan_filing_url(plan.id),
        )

    def test_that_relative_expiration_is_calculated_correctly(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self._create_active_plan(timeframe=5)
        view_model = self.presenter.present(self.response_with_one_active_plan(plan))
        self.assertEqual(
            view_model.active_plans.rows[0].expiration_relative,
            "5",
        )

    def test_that_drafts_are_not_shown_when_no_draft_is_in_response(self) -> None:
        response = self.response_with_no_plans()
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_drafts)

    def test_drafts_are_displayed_if_one_is_in_response(self) -> None:
        response = self.response_with_one_draft()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_drafts)

    def test_that_draft_prd_name_is_filled_in_correctly(self) -> None:
        expected_name = "test product name"
        response = self.response_with_one_draft(product_name=expected_name)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.drafts.rows[0].product_name, expected_name)

    def test_that_draft_creation_date_is_filled_in_correctly(self) -> None:
        expected_creation_time = datetime(2020, 5, 1)
        self.datetime_service.freeze_time(expected_creation_time)
        response = self.response_with_one_draft()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.drafts.rows[0].draft_creation_date, "01.05.20")

    def test_that_draft_details_url_is_set_correctly(self) -> None:
        response = self.response_with_one_draft()
        draft_id = response.drafts[0].id
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].draft_details_url,
            self.url_index.get_draft_details_url(draft_id),
        )

    def test_that_delete_draft_url_is_set_correctly(self) -> None:
        response = self.response_with_one_draft()
        draft_id = response.drafts[0].id
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].draft_delete_url,
            self.url_index.get_delete_draft_url(draft_id),
        )

    def test_that_file_plan_url_is_set_correctly(self) -> None:
        response = self.response_with_one_draft()
        draft_id = response.drafts[0].id
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].file_plan_url,
            self.url_index.get_file_plan_url(draft_id),
        )

    def test_that_edit_plan_url_is_set_correctly(self) -> None:
        response = self.response_with_one_draft()
        draft_id = response.drafts[0].id
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].edit_plan_url,
            self.url_index.get_draft_details_url(draft_id),
        )

    def test_do_only_show_rejected_plans_when_user_has_one_rejected_plan(self) -> None:
        plan = self.plan_generator.create_plan_record()
        RESPONSE_WITH_ONE_REJECTED_PLAN = self.response_with_one_rejected_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_REJECTED_PLAN)
        self.assertTrue(presentation.show_rejected_plans)
        self.assertFalse(presentation.show_expired_plans)
        self.assertFalse(presentation.show_non_active_plans)
        self.assertFalse(presentation.show_active_plans)

    def test_presenter_shows_correct_info_of_one_single_rejected_plan(self) -> None:
        plan = self.plan_generator.create_plan_record(cooperation=None)
        RESPONSE_WITH_ONE_REJECTED_PLAN = self.response_with_one_rejected_plan(plan)
        presentation = self.presenter.present(RESPONSE_WITH_ONE_REJECTED_PLAN)
        self.assertEqual(
            presentation.rejected_plans.rows[0].plan_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan.id
            ),
        )
        self.assertEqual(presentation.rejected_plans.rows[0].prd_name, plan.prd_name)
        self.assertEqual(
            presentation.rejected_plans.rows[0].price_per_unit,
            str("10.00"),
        )
        self.assertEqual(
            presentation.rejected_plans.rows[0].is_public_service,
            plan.is_public_service,
        )
        self.assertEqual(
            presentation.rejected_plans.rows[0].is_cooperating,
            False,
        )

    def _convert_into_plan_info(
        self, plan: Plan, cooperation: UUID | None = None
    ) -> PlanInfo:
        return PlanInfo(
            id=plan.id,
            prd_name=plan.prd_name,
            price_per_unit=Decimal("10.001"),
            is_public_service=plan.is_public_service,
            plan_creation_date=plan.plan_creation_date,
            activation_date=plan.activation_date,
            expiration_date=plan.expiration_date,
            is_cooperating=bool(cooperation),
            cooperation=cooperation,
            rejection_date=plan.rejection_date,
        )

    def _convert_draft_into_plan_info(self, plan: PlanDraft) -> PlanInfo:
        return PlanInfo(
            id=plan.id,
            prd_name=plan.product_name,
            price_per_unit=plan.production_costs.total_cost() / plan.amount_produced,
            is_public_service=plan.is_public_service,
            plan_creation_date=plan.creation_date,
            activation_date=None,
            expiration_date=None,
            is_cooperating=False,
            cooperation=None,
            rejection_date=None,
        )

    def response_with_one_draft(
        self, *, product_name: str = "test name"
    ) -> ShowMyPlansResponse:
        planner = self.company_generator.create_company()
        self.plan_generator.draft_plan(
            product_name=product_name, timeframe=1, planner=planner
        )
        self.datetime_service.advance_time(timedelta(days=2))
        return self.show_my_plans.show_company_plans(
            request=ShowMyPlansRequest(company_id=planner)
        )

    def response_with_no_plans(self) -> ShowMyPlansResponse:
        return ShowMyPlansResponse(
            count_all_plans=0,
            non_active_plans=[],
            active_plans=[],
            expired_plans=[],
            drafts=[],
            rejected_plans=[],
        )

    def response_with_one_plan(self, plan: Plan) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[],
            active_plans=[plan_info],
            expired_plans=[],
            drafts=[],
            rejected_plans=[],
        )

    def response_with_one_active_plan(
        self, plan: Plan, cooperation: UUID | None = None
    ) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan, cooperation)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[],
            active_plans=[plan_info],
            expired_plans=[],
            drafts=[],
            rejected_plans=[],
        )

    def response_with_one_expired_plan(self) -> ShowMyPlansResponse:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan_record(planner=planner, timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        return self.show_my_plans.show_company_plans(
            request=ShowMyPlansRequest(company_id=planner)
        )

    def response_with_one_non_active_plan(self, plan: Plan) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[plan_info],
            active_plans=[],
            expired_plans=[],
            drafts=[],
            rejected_plans=[],
        )

    def response_with_one_rejected_plan(self, plan: Plan) -> ShowMyPlansResponse:
        plan_info = self._convert_into_plan_info(plan)
        return ShowMyPlansResponse(
            count_all_plans=1,
            non_active_plans=[],
            active_plans=[],
            expired_plans=[],
            drafts=[],
            rejected_plans=[plan_info],
        )

    def _create_active_plan(self, timeframe: int = 1) -> Plan:
        plan = self.plan_generator.create_plan_record(
            timeframe=timeframe,
        )
        return plan
