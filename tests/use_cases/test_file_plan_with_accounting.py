from typing import Optional
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from tests.data_generators import PlanGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(FilePlanWithAccounting)
        self.plan_generator = self.injector.get(PlanGenerator)

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

    def create_request(
        self, draft: Optional[UUID] = None
    ) -> FilePlanWithAccounting.Request:
        if draft is None:
            draft = self.plan_generator.draft_plan().id
        return FilePlanWithAccounting.Request(draft_id=draft)
