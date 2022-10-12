from unittest import TestCase

from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase,
)
from tests.data_generators import PlanGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ListPlansWithPendingReviewUseCase)
        self.file_plan_with_accounting_use_case = self.injector.get(
            FilePlanWithAccounting
        )
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_no_plans_are_returned_if_none_was_created(self) -> None:
        request = ListPlansWithPendingReviewUseCase.Request()
        response = self.use_case.list_plans_with_pending_review(request=request)
        self.assertFalse(response.plans)

    def test_that_new_plan_with_pending_review_is_created_when_filing_a_draft(
        self,
    ) -> None:
        self.file_plan_draft()
        response = self.use_case.list_plans_with_pending_review(
            request=ListPlansWithPendingReviewUseCase.Request()
        )
        self.assertTrue(response.plans)

    def file_plan_draft(self) -> None:
        draft = self.plan_generator.draft_plan()
        request = FilePlanWithAccounting.Request(
            draft_id=draft.id, filing_company=draft.planner.id
        )
        self.file_plan_with_accounting_use_case.file_plan_with_accounting(request)
