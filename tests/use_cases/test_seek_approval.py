from datetime import datetime
from unittest import TestCase
from uuid import UUID

from arbeitszeit.use_cases import SeekApproval
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector
from .repositories import PlanDraftRepository, PlanRepository


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.seek_approval = self.injector.get(SeekApproval)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.draft_repository = self.injector.get(PlanDraftRepository)
        self.plan_repository = self.injector.get(PlanRepository)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_any_plan_will_be_approved(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        approval_response = self.seek_approval(
            SeekApproval.Request(draft_id=plan_draft.id)
        )
        assert approval_response.is_approved

    def test_plan_draft_gets_deleted_after_approval(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        response = self.seek_approval(SeekApproval.Request(draft_id=plan_draft.id))
        assert response.is_approved
        assert self.draft_repository.get_by_id(plan_draft.id) is None

    def test_that_true_is_returned(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        approval_response = self.seek_approval(
            SeekApproval.Request(draft_id=plan_draft.id)
        )
        assert approval_response.is_approved is True

    def test_that_returned_new_plan_id_is_uuid(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        approval_response = self.seek_approval(
            SeekApproval.Request(draft_id=plan_draft.id)
        )
        assert isinstance(approval_response.new_plan_id, UUID)

    def test_that_approval_date_has_correct_day_of_month(self) -> None:
        self.datetime_service.freeze_time(datetime(year=2021, month=5, day=3))
        plan_draft = self.plan_generator.draft_plan()
        self.seek_approval(SeekApproval.Request(draft_id=plan_draft.id))
        new_plan = self.plan_repository.get_plan_by_id(plan_draft.id)
        assert new_plan
        assert new_plan.approval_date
        assert 3 == new_plan.approval_date.day

    def test_that_approved_plan_has_same_planner_as_draft(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        self.seek_approval(SeekApproval.Request(draft_id=plan_draft.id))
        new_plan = self.plan_repository.get_plan_by_id(plan_draft.id)
        assert new_plan
        assert new_plan.planner == plan_draft.planner
