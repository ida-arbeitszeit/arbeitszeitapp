from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from arbeitszeit.use_cases.get_company_dashboard import (
    GetCompanyDashboardUseCase as UseCase,
)
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)
from tests.www.base_test_case import BaseTestCase


class CompanyDashboardBaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCompanyDashboardPresenter)

    def get_use_case_response(
        self,
        has_workers: bool = False,
        company_info: Optional[UseCase.Response.CompanyInfo] = None,
        latest_plans: Optional[List[UseCase.Response.LatestPlansDetails]] = None,
    ) -> UseCase.Response:
        if company_info is None:
            company_info = UseCase.Response.CompanyInfo(
                id=uuid4(), name="company name", email="mail@test.de"
            )
        if latest_plans is None:
            latest_plans = [
                UseCase.Response.LatestPlansDetails(
                    plan_id=uuid4(),
                    prd_name="prd name test",
                    approval_date=self.datetime_service.now(),
                )
            ]
        return UseCase.Response(
            company_info=company_info,
            has_workers=has_workers,
            three_latest_plans=latest_plans,
        )


class CompanyDashboardPresenterTests(CompanyDashboardBaseTestCase):
    def test_presenter_successfully_presents_a_use_case_response(self):
        self.assertTrue(self.presenter.present(self.get_use_case_response()))

    def test_presenter_correctly_shows_that_company_has_no_workers(self):
        has_workers = self.presenter.present(
            self.get_use_case_response(has_workers=False)
        ).has_workers
        self.assertFalse(has_workers)

    def test_presenter_correctly_shows_company_name(self):
        view_model = self.presenter.present(
            self.get_use_case_response(
                company_info=UseCase.Response.CompanyInfo(
                    id=uuid4(), name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_name, "company test name")

    def test_presenter_correctly_shows_company_id(self):
        company_id = uuid4()
        view_model = self.presenter.present(
            self.get_use_case_response(
                company_info=UseCase.Response.CompanyInfo(
                    id=company_id, name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_id, str(company_id))

    def test_presenter_correctly_shows_company_email(self):
        view_model = self.presenter.present(
            self.get_use_case_response(
                company_info=UseCase.Response.CompanyInfo(
                    id=uuid4(), name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_email, "mail@test.de")

    def test_presenter_correctly_shows_that_there_are_no_latest_plans_to_show(self):
        view_model = self.presenter.present(self.get_use_case_response(latest_plans=[]))
        self.assertFalse(view_model.has_latest_plans)

    def test_presenter_correctly_shows_that_there_are_latest_plans_to_show(self):
        view_model = self.presenter.present(self.get_use_case_response())
        self.assertTrue(view_model.has_latest_plans)

    def test_presenter_correctly_formats_date_of_latest_plans(self):
        self.datetime_service.freeze_time(datetime(2022, 1, 1))
        approval_time = self.datetime_service.now()
        view_model = self.presenter.present(
            self.get_use_case_response(
                latest_plans=[
                    UseCase.Response.LatestPlansDetails(
                        plan_id=uuid4(),
                        prd_name="prd name test",
                        approval_date=approval_time,
                    )
                ]
            )
        )
        self.assertEqual(view_model.latest_plans[0].approval_date, "01.01.")

    def test_presenter_shows_correct_link_to_latest_plan(self):
        plan_id = uuid4()
        view_model = self.presenter.present(
            self.get_use_case_response(
                latest_plans=[
                    UseCase.Response.LatestPlansDetails(
                        plan_id=plan_id,
                        prd_name="prd name test",
                        approval_date=self.datetime_service.now(),
                    )
                ]
            )
        )
        self.assertEqual(
            view_model.latest_plans[0].plan_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan_id
            ),
        )


class CompanyDashboardTileTests(CompanyDashboardBaseTestCase):
    def test_accounts_tile_has_correct_title(self) -> None:
        view_model = self.presenter.present(self.get_use_case_response())
        self.assertEqual(
            view_model.accounts_tile.title, self.translator.gettext("Accounts")
        )

    def test_accounts_tile_has_correct_subtitle(self) -> None:
        view_model = self.presenter.present(self.get_use_case_response())
        self.assertEqual(
            view_model.accounts_tile.subtitle,
            self.translator.gettext("You have four accounts"),
        )

    def test_accounts_tile_has_correct_icon(self) -> None:
        view_model = self.presenter.present(self.get_use_case_response())
        self.assertEqual(view_model.accounts_tile.icon, "chart-line")

    def test_accounts_tile_has_url_that_leads_to_accounts_of_company_from_use_case_response(
        self,
    ) -> None:
        expected_company_id = uuid4()
        view_model = self.presenter.present(
            self.get_use_case_response(
                company_info=UseCase.Response.CompanyInfo(
                    id=expected_company_id,
                    name="company test name",
                    email="mail@test.de",
                )
            )
        )
        self.assertEqual(
            view_model.accounts_tile.url,
            self.url_index.get_company_accounts_url(company_id=expected_company_id),
        )
