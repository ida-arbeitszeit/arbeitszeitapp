from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import GetPlanSummaryCompany
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


class Tests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.get_plan_summary_company = self.injector.get(GetPlanSummaryCompany)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_current_user_is_correctly_shown_as_planner(self):
        planner_and_current_user = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(planner=planner_and_current_user)
        response = self.get_plan_summary_company.get_plan_summary_for_company(
            plan.id, planner_and_current_user.id
        )
        assert isinstance(response, GetPlanSummaryCompany.Response)
        assert response.current_user_is_planner

    def test_that_current_user_is_correctly_shown_as_non_planner(self):
        current_user = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan()
        response = self.get_plan_summary_company.get_plan_summary_for_company(
            plan.id, current_user.id
        )
        assert not response.current_user_is_planner

    def test_that_plan_summary_is_none_if_plan_does_not_exist(self):
        current_user = self.company_generator.create_company_entity()
        response = self.get_plan_summary_company.get_plan_summary_for_company(
            uuid4(), current_user.id
        )
        self.assertIsNone(response.plan_summary)

    def test_plan_summary_success_is_returned_when_plan_exists(self):
        current_user = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan()
        self.assertIsInstance(
            self.get_plan_summary_company.get_plan_summary_for_company(
                plan.id, current_user.id
            ),
            GetPlanSummaryCompany.Response,
        )

    def test_plan_summary_is_returned_when_plan_exists(self):
        current_user = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan()
        plan_summary_success = (
            self.get_plan_summary_company.get_plan_summary_for_company(
                plan.id, current_user.id
            )
        )
        assert isinstance(plan_summary_success, GetPlanSummaryCompany.Response)
        self.assertTrue(plan_summary_success.plan_summary)
