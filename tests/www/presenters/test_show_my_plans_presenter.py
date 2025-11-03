from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.interactors.show_my_plans import (
    PlanInfo,
    ShowMyPlansResponse,
)
from arbeitszeit_web.www.presenters.show_my_plans_presenter import ShowMyPlansPresenter
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase


class PresenterBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowMyPlansPresenter)

    def create_plan_info(
        self,
        plan_id: UUID | None = None,
        prd_name: str = "Product name",
        price_per_unit: Decimal = Decimal(10),
        is_public_service: bool = False,
        plan_creation_date: datetime = datetime_utc(2020, 1, 1),
        approval_date: datetime | None = None,
        expiration_date: datetime | None = None,
        rejection_date: datetime | None = None,
        is_cooperating: bool = False,
        cooperation: UUID | None = None,
    ) -> PlanInfo:
        if plan_id is None:
            plan_id = uuid4()
        return PlanInfo(
            id=plan_id,
            prd_name=prd_name,
            price_per_unit=price_per_unit,
            is_public_service=is_public_service,
            plan_creation_date=plan_creation_date,
            approval_date=approval_date,
            expiration_date=expiration_date,
            rejection_date=rejection_date,
            is_cooperating=is_cooperating,
            cooperation=cooperation,
        )

    def create_interactor_response(
        self,
        num_of_plans: int = 0,
        non_active_plans: list[PlanInfo] | None = None,
        active_plans: list[PlanInfo] | None = None,
        expired_plans: list[PlanInfo] | None = None,
        drafts: list[PlanInfo] | None = None,
        rejected_plans: list[PlanInfo] | None = None,
    ) -> ShowMyPlansResponse:
        if non_active_plans is None:
            non_active_plans = []
        if active_plans is None:
            active_plans = []
        if expired_plans is None:
            expired_plans = []
        if drafts is None:
            drafts = []
        if rejected_plans is None:
            rejected_plans = []
        return ShowMyPlansResponse(
            count_all_plans=num_of_plans,
            non_active_plans=non_active_plans,
            active_plans=active_plans,
            expired_plans=expired_plans,
            drafts=drafts,
            rejected_plans=rejected_plans,
        )


class ShowMyPlansPresenterTests(PresenterBase):
    def test_show_correct_notification_when_user_has_no_plans(self) -> None:
        response = self.create_interactor_response(num_of_plans=0)
        self.presenter.present(response)
        assert self.notifier.infos == [
            self.translator.gettext("You don't have any plans.")
        ]

    def test_show_no_notification_when_user_has_one_plan(self) -> None:
        response = self.create_interactor_response(num_of_plans=1)
        self.presenter.present(response)
        self.assertFalse(self.notifier.infos)
        self.assertFalse(self.notifier.warnings)


class ActivePlansTests(PresenterBase):
    def test_do_only_show_active_plans_when_user_has_one_active_plan(self) -> None:
        response = self.create_interactor_response(
            num_of_plans=1, active_plans=[self.create_plan_info()]
        )
        presentation = self.presenter.present(response)
        assert presentation.show_active_plans
        assert not presentation.show_expired_plans
        assert not presentation.show_non_active_plans
        assert not presentation.show_rejected_plans

    def test_presenter_shows_correct_info_of_active_plan(self) -> None:
        PLAN_ID = uuid4()
        PRD_NAME = "Some product name"
        PRICE_PER_UNIT = Decimal(10)
        IS_PUBLIC_SERVICE = True
        response = self.create_interactor_response(
            active_plans=[
                self.create_plan_info(
                    plan_id=PLAN_ID,
                    prd_name=PRD_NAME,
                    price_per_unit=PRICE_PER_UNIT,
                    is_public_service=IS_PUBLIC_SERVICE,
                )
            ]
        )
        presentation = self.presenter.present(response)
        row = presentation.active_plans.rows[0]
        assert row.plan_details_url == self.url_index.get_plan_details_url(
            user_role=None, plan_id=PLAN_ID
        )
        assert row.prd_name == PRD_NAME
        assert row.price_per_unit == "10.00"
        assert row.is_public_service == IS_PUBLIC_SERVICE

    @parameterized.expand([(True,), (False,)])
    def test_presenter_shows_correct_cooperating_status_of_active_plan(
        self, is_cooperating: bool
    ) -> None:
        response = self.create_interactor_response(
            active_plans=[
                self.create_plan_info(
                    is_cooperating=is_cooperating,
                )
            ]
        )
        presentation = self.presenter.present(response)
        assert presentation.active_plans.rows[0].is_cooperating == is_cooperating

    @parameterized.expand([(datetime_utc(2020, 5, 1, 10, 30),), (None,)])
    def test_presenter_shows_correct_expiration_date_of_active_plan(
        self, expiration_date: datetime | None
    ) -> None:
        response = self.create_interactor_response(
            active_plans=[
                self.create_plan_info(
                    expiration_date=expiration_date,
                )
            ]
        )
        presentation = self.presenter.present(response)
        assert (
            presentation.active_plans.rows[0].expiration_date
            == expiration_date.strftime("%d.%m.%y")
            if expiration_date
            else "–"
        )

    @parameterized.expand([(datetime_utc(2000, 1, 6),), (None,)])
    def test_that_relative_expiration_is_calculated_correctly_in_days_from_now(
        self, expiration_date: datetime | None
    ) -> None:
        now = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(now)
        response = self.create_interactor_response(
            active_plans=[
                self.create_plan_info(
                    expiration_date=expiration_date,
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert (
            view_model.active_plans.rows[0].expiration_relative == "5"
            if expiration_date
            else "-"
        )


class ExpiredPlansTests(PresenterBase):
    def test_presenter_shows_correct_info_of_expired_plan(self) -> None:
        PLAN_ID = uuid4()
        PRD_NAME = "Some product name"
        IS_PUBLIC_SERVICE = True
        response = self.create_interactor_response(
            expired_plans=[
                self.create_plan_info(
                    plan_id=PLAN_ID,
                    prd_name=PRD_NAME,
                    is_public_service=IS_PUBLIC_SERVICE,
                )
            ]
        )
        presentation = self.presenter.present(response)
        row = presentation.expired_plans.rows[0]
        self.assertEqual(
            row.plan_details_url,
            self.url_index.get_plan_details_url(user_role=None, plan_id=PLAN_ID),
        )
        self.assertEqual(
            row.prd_name,
            PRD_NAME,
        )
        self.assertEqual(row.is_public_service, IS_PUBLIC_SERVICE)
        self.assertEqual(
            row.renew_plan_url,
            self.url_index.get_renew_plan_url(PLAN_ID),
        )
        self.assertEqual(
            row.hide_plan_url,
            self.url_index.get_hide_plan_url(PLAN_ID),
        )


class NonActivePlansTests(PresenterBase):
    def test_presenter_shows_correct_info_of_non_active_plan(self) -> None:
        PLAN_ID = uuid4()
        PRD_NAME = "Some product name"
        PRICE_PER_UNIT = Decimal(22)
        response = self.create_interactor_response(
            non_active_plans=[
                self.create_plan_info(
                    plan_id=PLAN_ID, prd_name=PRD_NAME, price_per_unit=PRICE_PER_UNIT
                )
            ]
        )
        presentation = self.presenter.present(response)
        row = presentation.non_active_plans.rows[0]
        self.assertEqual(
            row.plan_details_url,
            self.url_index.get_plan_details_url(user_role=None, plan_id=PLAN_ID),
        )
        self.assertEqual(
            row.prd_name,
            PRD_NAME,
        )
        self.assertEqual(
            row.price_per_unit,
            str(round(PRICE_PER_UNIT, 2)),
        )

    @parameterized.expand([(True,), (False,)])
    def test_presenter_converts_public_status_of_non_active_plan_in_correct_string(
        self, is_public_service: bool
    ) -> None:
        response = self.create_interactor_response(
            non_active_plans=[
                self.create_plan_info(is_public_service=is_public_service)
            ]
        )
        presentation = self.presenter.present(response)
        assert (
            presentation.non_active_plans.rows[0].type_of_plan
            == self.translator.gettext("Public")
            if is_public_service
            else self.translator.gettext("Productive")
        )

    def test_non_active_plan_has_correct_revocation_url(self) -> None:
        PLAN_ID = uuid4()
        response = self.create_interactor_response(
            non_active_plans=[
                self.create_plan_info(
                    plan_id=PLAN_ID,
                )
            ]
        )
        view_model = self.presenter.present(response)
        row = view_model.non_active_plans.rows[0]
        self.assertEqual(
            row.revoke_plan_filing_url,
            self.url_index.get_revoke_plan_filing_url(PLAN_ID),
        )


class DraftsTests(PresenterBase):
    def test_that_drafts_are_not_shown_when_no_draft_is_in_response(self) -> None:
        response = self.create_interactor_response()
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_drafts)

    def test_drafts_are_displayed_if_one_is_in_response(self) -> None:
        response = self.create_interactor_response(drafts=[self.create_plan_info()])
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_drafts)

    def test_that_draft_prd_name_is_filled_in_correctly(self) -> None:
        PRD_NAME = "test product name"
        response = self.create_interactor_response(
            drafts=[self.create_plan_info(prd_name=PRD_NAME)]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.drafts.rows[0].product_name, PRD_NAME)

    def test_that_draft_creation_date_is_filled_in_correctly(self) -> None:
        CREATION_DATE = datetime_utc(2020, 5, 1)
        response = self.create_interactor_response(
            drafts=[self.create_plan_info(plan_creation_date=CREATION_DATE)]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.drafts.rows[0].draft_creation_date, "01.05.20")

    def test_that_draft_details_url_is_set_correctly(self) -> None:
        DRAFT_ID = uuid4()
        response = self.create_interactor_response(
            drafts=[self.create_plan_info(plan_id=DRAFT_ID)]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].draft_details_url,
            self.url_index.get_draft_details_url(DRAFT_ID),
        )

    def test_that_delete_draft_url_is_set_correctly(self) -> None:
        DRAFT_ID = uuid4()
        response = self.create_interactor_response(
            drafts=[self.create_plan_info(plan_id=DRAFT_ID)]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].draft_delete_url,
            self.url_index.get_delete_draft_url(DRAFT_ID),
        )

    def test_that_file_plan_url_is_set_correctly(self) -> None:
        DRAFT_ID = uuid4()
        response = self.create_interactor_response(
            drafts=[self.create_plan_info(plan_id=DRAFT_ID)]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].file_plan_url,
            self.url_index.get_file_plan_url(DRAFT_ID),
        )

    def test_that_edit_plan_url_is_set_correctly(self) -> None:
        DRAFT_ID = uuid4()
        response = self.create_interactor_response(
            drafts=[self.create_plan_info(plan_id=DRAFT_ID)]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.drafts.rows[0].edit_plan_url,
            self.url_index.get_draft_details_url(DRAFT_ID),
        )


class RejectedPlansTests(PresenterBase):
    def test_do_only_show_rejected_plans_when_user_has_one_rejected_plan(self) -> None:
        response = self.create_interactor_response(
            rejected_plans=[self.create_plan_info()]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_rejected_plans)
        self.assertFalse(presentation.show_expired_plans)
        self.assertFalse(presentation.show_non_active_plans)
        self.assertFalse(presentation.show_active_plans)

    def test_presenter_shows_correct_info_of_one_single_rejected_plan(self) -> None:
        PLAN_ID = uuid4()
        PRD_NAME = "Some product name"
        PRICE_PER_UNIT = Decimal(33)
        IS_PUBLIC_SERVICE = True
        response = self.create_interactor_response(
            rejected_plans=[
                self.create_plan_info(
                    plan_id=PLAN_ID,
                    prd_name=PRD_NAME,
                    price_per_unit=PRICE_PER_UNIT,
                    is_public_service=IS_PUBLIC_SERVICE,
                )
            ]
        )
        presentation = self.presenter.present(response)
        row = presentation.rejected_plans.rows[0]
        self.assertEqual(
            row.plan_details_url,
            self.url_index.get_plan_details_url(user_role=None, plan_id=PLAN_ID),
        )
        self.assertEqual(row.prd_name, PRD_NAME)
        self.assertEqual(
            row.price_per_unit,
            str(round(PRICE_PER_UNIT, 2)),
        )
        self.assertEqual(
            row.is_public_service,
            IS_PUBLIC_SERVICE,
        )
