from datetime import datetime, timedelta
from uuid import uuid4

from arbeitszeit.use_cases import ShowMyPlansRequest, ShowMyPlansUseCase
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ShowMyPlansUseCase)

    def test_that_no_plans_are_returned_when_no_plans_were_created(self) -> None:
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=uuid4())
        )
        assert not response.count_all_plans

    def test_that_one_approved_plan_is_returned_after_one_plan_was_created(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        assert response.count_all_plans == 1

    def test_that_no_plans_for_a_company_without_plans_are_found(self) -> None:
        company = self.company_generator.create_company_entity()
        other_company = self.company_generator.create_company_entity()
        self.plan_generator.create_plan(approved=True, planner=company)
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=other_company.id)
        )
        assert not response.count_all_plans

    def test_that_with_one_draft_that_plan_count_is_one(self) -> None:
        company = self.company_generator.create_company_entity()
        self.plan_generator.draft_plan(planner=company)
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        self.assertEqual(response.count_all_plans, 1)

    def test_that_with_no_drafts_that_drafts_in_response_is_empty(self) -> None:
        company = self.company_generator.create_company_entity()
        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        self.assertFalse(response.drafts)

    def test_that_drafts_are_returned_in_correct_order(self) -> None:
        creation_time_1 = datetime(2020, 5, 1, 20)
        creation_time_2 = creation_time_1 - timedelta(hours=5)
        creation_time_3 = creation_time_1 + timedelta(days=2)

        company = self.company_generator.create_company_entity()

        self.datetime_service.freeze_time(creation_time_2)
        expected_third_plan = self.plan_generator.draft_plan(planner=company)
        self.datetime_service.freeze_time(creation_time_1)
        expected_second_plan = self.plan_generator.draft_plan(planner=company)
        self.datetime_service.freeze_time(creation_time_3)
        expected_first_plan = self.plan_generator.draft_plan(planner=company)

        response = self.use_case.show_company_plans(
            request=ShowMyPlansRequest(company_id=company.id)
        )
        self.assertEqual(response.drafts[0].id, expected_first_plan.id)
        self.assertEqual(response.drafts[1].id, expected_second_plan.id)
        self.assertEqual(response.drafts[2].id, expected_third_plan.id)
