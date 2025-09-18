from datetime import timedelta
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.interactors.get_company_dashboard import GetCompanyDashboardInteractor
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService, datetime_utc
from tests.interactors.dependency_injection import get_dependency_injector


class GeneralInteractorTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.interactor = self.injector.get(GetCompanyDashboardInteractor)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_retrieving_dashboard_for_nonexisting_company_fails(self) -> None:
        with self.assertRaises(GetCompanyDashboardInteractor.Failure):
            self.interactor.get_dashboard(uuid4())

    def test_that_retrieving_dashboard_for_existing_company_succeeds(self) -> None:
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertIsInstance(response, GetCompanyDashboardInteractor.Response)

    def test_that_dashboard_shows_company_name(self) -> None:
        expected_name = "test coop name"
        company = self.company_generator.create_company_record(name=expected_name)
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.company_info.name, expected_name)

    def test_that_dashboard_shows_company_id(self) -> None:
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.company_info.id, company.id)

    def test_that_dashboard_shows_company_email(self) -> None:
        expected_mail = "t@tmail.com"
        company = self.company_generator.create_company_record(email=expected_mail)
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.company_info.email, expected_mail)

    def test_that_dashboard_shows_that_company_has_no_workers(self) -> None:
        company = self.company_generator.create_company_record(workers=None)
        response = self.interactor.get_dashboard(company.id)
        self.assertFalse(response.has_workers)

    def test_that_dashboard_shows_that_company_has_workers(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.interactor.get_dashboard(company.id)
        self.assertTrue(response.has_workers)


class ThreeLatestPlansTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.interactor = self.injector.get(GetCompanyDashboardInteractor)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_list_of_latest_plans_is_empty_when_there_are_no_plans(self) -> None:
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertFalse(response.three_latest_plans)

    def test_that_list_of_latest_plans_has_three_entries_when_there_are_five_active_plans(
        self,
    ) -> None:
        for _ in range(5):
            self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(len(response.three_latest_plans), 3)

    def test_that_plan_id_of_latest_plan_is_set_correctly(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.three_latest_plans[0].plan_id, plan)

    def test_that_product_name_of_latest_plan_is_set_correctly(
        self,
    ) -> None:
        expected_name = "test product xy"
        self.plan_generator.create_plan(product_name=expected_name)
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.three_latest_plans[0].prd_name, expected_name)

    def test_that_approval_date_of_latest_plan_is_set_correctly(
        self,
    ) -> None:
        expected_datetime = datetime_utc(2020, 10, 10)
        self.datetime_service.freeze_time(expected_datetime)
        self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(hours=1))
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(
            response.three_latest_plans[0].approval_date, expected_datetime
        )
