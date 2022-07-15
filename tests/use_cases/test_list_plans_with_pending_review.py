from unittest import TestCase

from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase,
)

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ListPlansWithPendingReviewUseCase)

    def test_that_no_plans_are_returned_if_none_was_created(self) -> None:
        request = ListPlansWithPendingReviewUseCase.Request()
        response = self.use_case.list_plans_with_pending_review(request=request)
        self.assertFalse(response.plans)
