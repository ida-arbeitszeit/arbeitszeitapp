from datetime import datetime
from typing import List
from unittest import TestCase
from uuid import uuid4
from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit_web.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)
from tests.datetime_service import FakeDatetimeService

from tests.presenters.dependency_injection import get_dependency_injector
from tests.presenters.url_index import PlanSummaryUrlIndexTestImpl


class TestPresenter(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(GetCompanyDashboardPresenter)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.plan_index = self.injector.get(PlanSummaryUrlIndexTestImpl)

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
                company_info=GetCompanyDashboardUseCase.Success.CompanyInfo(
                    id=uuid4(), name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_name, "company test name")

    def test_presenter_correctly_shows_company_id(self):
        company_id = uuid4()
        view_model = self.presenter.present(
            self.get_use_case_response(
                company_info=GetCompanyDashboardUseCase.Success.CompanyInfo(
                    id=company_id, name="company test name", email="mail@test.de"
                )
            )
        )
        self.assertEqual(view_model.company_id, str(company_id))

    def test_presenter_correctly_shows_company_email(self):
        view_model = self.presenter.present(
            self.get_use_case_response(
                company_info=GetCompanyDashboardUseCase.Success.CompanyInfo(
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
        activation_time = self.datetime_service.now()
        view_model = self.presenter.present(
            self.get_use_case_response(
                latest_plans=[
                    GetCompanyDashboardUseCase.Success.LatestPlansDetails(
                        plan_id=uuid4(),
                        prd_name="prd name test",
                        activation_date=activation_time,
                    )
                ]
            )
        )
        self.assertEqual(view_model.latest_plans[0].activation_date, "01.01.")

    def test_presenter_shows_correct_link_to_latest_plan(self):
        plan_id = uuid4()
        view_model = self.presenter.present(
            self.get_use_case_response(
                latest_plans=[
                    GetCompanyDashboardUseCase.Success.LatestPlansDetails(
                        plan_id=plan_id,
                        prd_name="prd name test",
                        activation_date=self.datetime_service.now(),
                    )
                ]
            )
        )
        self.assertEqual(
            view_model.latest_plans[0].plan_summary_url,
            self.plan_index.get_plan_summary_url(plan_id),
        )

    def get_use_case_response(
        self,
        has_workers: bool = None,
        company_info: GetCompanyDashboardUseCase.Success.CompanyInfo = None,
        latest_plans: List[
            GetCompanyDashboardUseCase.Success.LatestPlansDetails
        ] = None,
    ):
        if has_workers is None:
            has_workers = False
        if company_info is None:
            company_info = GetCompanyDashboardUseCase.Success.CompanyInfo(
                id=uuid4(), name="company name", email="mail@test.de"
            )
        if latest_plans is None:
            latest_plans = [
                GetCompanyDashboardUseCase.Success.LatestPlansDetails(
                    plan_id=uuid4(),
                    prd_name="prd name test",
                    activation_date=self.datetime_service.now(),
                )
            ]
        return GetCompanyDashboardUseCase.Success(
            company_info=company_info,
            has_workers=has_workers,
            three_latest_plans=latest_plans,
        )
