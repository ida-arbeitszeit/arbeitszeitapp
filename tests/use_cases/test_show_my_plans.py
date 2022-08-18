from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import ShowMyPlansRequest, ShowMyPlansUseCase

from ..data_generators import CompanyGenerator, PlanGenerator
from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ShowMyPlansUseCase)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_no_plans_are_returned_when_no_plans_were_created(self) -> None:
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=uuid4())
        )
        assert not response.count_all_plans

    def test_that_one_approved_plan_is_returned_after_one_plan_was_created(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        assert response.count_all_plans == 1

    def test_that_no_plans_for_a_company_without_plans_are_found(self) -> None:
        company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.plan_generator.create_plan(approved=True, planner=company)
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=other_company.id)
        )
        assert not response.count_all_plans

    def test_that_with_one_draft_that_plan_count_is_one(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.draft_plan(planner=company)
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        self.assertEqual(response.count_all_plans, 1)

    def test_that_with_no_drafts_that_drafts_in_response_is_empty(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        self.assertFalse(response.drafts)
