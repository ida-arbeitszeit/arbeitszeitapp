from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.use_cases.dependency_injection import get_dependency_injector


class GeneralUseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(GetCompanyDashboardUseCase)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_retrieving_dashboard_for_nonexisting_company_fails(self):
        response = self.use_case.get_dashboard(uuid4())
        self.assertIsInstance(response, GetCompanyDashboardUseCase.Failure)

    def test_that_retrieving_dashboard_for_existing_company_succeeds(self):
        company = self.company_generator.create_company()
        response = self.use_case.get_dashboard(company.id)
        self.assertIsInstance(response, GetCompanyDashboardUseCase.Success)

    def test_that_dashboard_shows_company_name(self):
        company = self.company_generator.create_company(name="test coop name")
        response = self.use_case.get_dashboard(company.id)
        self.assertEqual(response.company_info.name, company.name)

    def test_that_dashboard_shows_company_id(self):
        company = self.company_generator.create_company()
        response = self.use_case.get_dashboard(company.id)
        self.assertEqual(response.company_info.id, company.id)

    def test_that_dashboard_shows_company_email(self):
        company = self.company_generator.create_company(email="t@tmail.com")
        response = self.use_case.get_dashboard(company.id)
        self.assertEqual(response.company_info.email, company.email)

    def test_that_dashboard_shows_that_company_has_no_workers(self):
        company = self.company_generator.create_company(workers=None)
        response = self.use_case.get_dashboard(company.id)
        self.assertFalse(response.has_workers)

    def test_that_dashboard_shows_that_company_has_workers(self):
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        response = self.use_case.get_dashboard(company.id)
        self.assertTrue(response.has_workers)


class ThreeLatestPlansTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(GetCompanyDashboardUseCase)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_list_of_latest_plans_is_empty_when_there_are_no_plans(self):
        company = self.company_generator.create_company()
        response = self.use_case.get_dashboard(company.id)
        self.assertFalse(response.three_latest_plans)

    def test_that_list_of_latest_plans_is_emtpy_when_there_is_one_inactive_plan(
        self,
    ):
        plan = self.plan_generator.create_plan()
        assert not plan.is_active
        company = self.company_generator.create_company()
        response = self.use_case.get_dashboard(company.id)
        self.assertFalse(response.three_latest_plans)

    def test_that_list_of_latest_plans_has_one_entry_when_there_is_one_active_plan(
        self,
    ):
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        company = self.company_generator.create_company()
        response = self.use_case.get_dashboard(company.id)
        self.assertEqual(len(response.three_latest_plans), 1)

    def test_that_list_of_latest_plans_has_three_entries_when_there_are_five_active_plans(
        self,
    ):
        for _ in range(5):
            self.plan_generator.create_plan(
                activation_date=self.datetime_service.now_minus_one_day()
            )
        company = self.company_generator.create_company()
        response = self.use_case.get_dashboard(company.id)
        self.assertEqual(len(response.three_latest_plans), 3)

    def test_returns_three_active_plans_in_correct_order(self):
        company = self.company_generator.create_company()
        timestamps = [
            None,
            self.datetime_service.now_minus_two_days(),
            self.datetime_service.now_minus_one_day(),  # second latest
            self.datetime_service.now_minus_ten_days(),
            self.datetime_service.now_minus_20_hours(),  # latest
            self.datetime_service.now_minus_25_hours(),  # third latest
        ]
        unordered_plans = [
            self.plan_generator.create_plan(activation_date=t) for t in timestamps
        ]
        response = self.use_case.get_dashboard(company.id)
        self.assertEqual(response.three_latest_plans[0].plan_id, unordered_plans[4].id)
        self.assertEqual(response.three_latest_plans[1].plan_id, unordered_plans[2].id)
        self.assertEqual(response.three_latest_plans[2].plan_id, unordered_plans[5].id)
