from datetime import datetime
from decimal import Decimal
from typing import Callable, Optional, cast
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember
from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase,
)
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(FilePlanWithAccounting)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.list_plans_with_pending_review_use_case = self.injector.get(
            ListPlansWithPendingReviewUseCase
        )
        self.get_plan_summary_member_use_case = self.injector.get(GetPlanSummaryMember)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.planner = self.company_generator.create_company()

    def test_that_filing_a_plan_with_a_random_draft_id_is_rejected(self) -> None:
        request = self.create_request(draft=uuid4())
        response = self.use_case.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_can_file_a_regular_plan_draft_with_accounting(self) -> None:
        request = self.create_request()
        response = self.use_case.file_plan_with_accounting(request)
        self.assertTrue(response.is_plan_successfully_filed)

    def test_that_the_same_draft_cannot_be_filed_twice(self) -> None:
        request = self.create_request()
        self.use_case.file_plan_with_accounting(request)
        response = self.use_case.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_that_response_contains_a_plan_id_when_a_valid_draft_is_provided(
        self,
    ) -> None:
        request = self.create_request()
        response = self.use_case.file_plan_with_accounting(request)
        self.assertIsNotNone(response.plan_id)

    def test_that_response_does_not_contain_plan_id_if_no_valid_draft_was_provided(
        self,
    ) -> None:
        request = self.create_request(draft=uuid4())
        response = self.use_case.file_plan_with_accounting(request)
        self.assertIsNone(response.plan_id)

    def test_that_we_can_retrieve_plan_details_for_a_plan_that_was_filed(self) -> None:
        request = self.create_request()
        response = self.use_case.file_plan_with_accounting(request)
        assert response.plan_id
        self.assertPlanSummaryIsAvailable(plan=response.plan_id)

    def test_that_product_name_is_correct_in_newly_created_plan(self) -> None:
        expected_product_name = "test product name"
        draft = self.create_draft(product_name=expected_product_name)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.product_name == expected_product_name,
        )

    def test_that_description_is_correct_in_newly_created_plan(self) -> None:
        expected_description = "test description"
        draft = self.create_draft(description=expected_description)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.description == expected_description,
        )

    def test_that_costs_are_correct_in_newly_created_plan(self) -> None:
        expected_costs = ProductionCosts(
            labour_cost=Decimal(5), resource_cost=Decimal(6), means_cost=Decimal(7)
        )
        draft = self.create_draft(costs=expected_costs)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.means_cost == expected_costs.means_cost,
        )
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.labour_cost == expected_costs.labour_cost,
        )
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.resources_cost == expected_costs.resource_cost,
        )

    def test_that_production_unit_is_correct_in_newly_created_plan(self) -> None:
        expected_unit = "test unit"
        draft = self.create_draft(production_unit=expected_unit)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.production_unit == expected_unit,
        )

    def test_that_timeframe_is_correct_in_newly_created_plan(self) -> None:
        expected_timeframe = 7
        draft = self.create_draft(timeframe=expected_timeframe)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id, condition=lambda s: s.timeframe == expected_timeframe
        )

    def test_that_amount_is_correct_in_newly_created_plan(self) -> None:
        expected_amount = 23
        draft = self.create_draft(amount=expected_amount)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id, condition=lambda s: s.amount == expected_amount
        )

    def test_that_creation_timestamp_is_set_to_time_of_filing_the_plan(self) -> None:
        expected_timestamp = datetime(2000, 2, 1)
        self.datetime_service.freeze_time(expected_timestamp)
        draft = self.create_draft()
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id, condition=lambda s: s.creation_date == expected_timestamp
        )

    def test_that_filed_plan_is_pulic_service_if_draft_was_also_for_public_service(
        self,
    ) -> None:
        draft = self.create_draft(is_public_service=True)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(plan=plan_id, condition=lambda s: s.is_public_service)

    def test_that_filed_plan_is_not_pulic_service_if_draft_was_also_not_for_public_service(
        self,
    ) -> None:
        draft = self.create_draft(is_public_service=False)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id, condition=lambda s: not s.is_public_service
        )

    def test_if_company_that_is_not_creator_of_craft_tries_to_file_a_draft_then_it_does_not_show_in_list_of_pending_reviews(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company()
        request = self.create_request(draft=draft, filing_company=other_company.id)
        self.use_case.file_plan_with_accounting(request)
        response = (
            self.list_plans_with_pending_review_use_case.list_plans_with_pending_review(
                ListPlansWithPendingReviewUseCase.Request()
            )
        )
        self.assertFalse(response.plans)

    def file_draft(self, draft: UUID) -> UUID:
        request = self.create_request(draft=draft)
        response = self.use_case.file_plan_with_accounting(request)
        assert response.plan_id
        return response.plan_id

    def create_draft(
        self,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        costs: Optional[ProductionCosts] = None,
        production_unit: Optional[str] = None,
        amount: Optional[int] = None,
        is_public_service: Optional[bool] = None,
        timeframe: Optional[int] = None,
    ) -> UUID:
        draft = self.plan_generator.draft_plan(
            product_name=product_name,
            description=description,
            costs=costs,
            production_unit=production_unit,
            amount=amount,
            is_public_service=is_public_service,
            timeframe=timeframe,
            planner=self.planner,
        )
        return draft.id

    def create_request(
        self,
        draft: Optional[UUID] = None,
        filing_company: Optional[UUID] = None,
    ) -> FilePlanWithAccounting.Request:
        if filing_company is None:
            filing_company = self.planner.id
        if draft is None:
            draft = self.create_draft()
        return FilePlanWithAccounting.Request(
            draft_id=draft, filing_company=filing_company
        )

    def assertPlanSummaryIsAvailable(self, plan: UUID) -> None:
        response = self.get_plan_summary_member_use_case(plan_id=plan)
        self.assertIsInstance(
            response,
            GetPlanSummaryMember.Success,
            msg=f"Plan summary for plan {plan} is not available",
        )

    def assertPlanSummary(
        self, plan: UUID, condition: Callable[[PlanSummary], bool]
    ) -> None:
        response = self.get_plan_summary_member_use_case(plan_id=plan)
        self.assertIsInstance(
            response,
            GetPlanSummaryMember.Success,
            msg=f"Plan summary for plan {plan} is not available",
        )
        summary = cast(GetPlanSummaryMember.Success, response).plan_summary
        self.assertTrue(condition(summary), msg=f"{summary}")
