from datetime import datetime
from uuid import UUID

from arbeitszeit.repositories import PlanDraftRepository, PlanRepository
from arbeitszeit.use_cases import SeekApproval
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


@injection_test
def test_that_any_plan_will_be_approved(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    plan_draft = plan_generator.draft_plan()
    approval_response = seek_approval(plan_draft.id)
    assert approval_response.is_approved


@injection_test
def test_plan_draft_gets_deleted_after_approval(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
    draft_repository: PlanDraftRepository,
):
    draft = plan_generator.draft_plan()
    response = seek_approval(
        draft.id,
    )
    assert response.is_approved
    assert draft_repository.get_by_id(draft.id) is None


@injection_test
def test_that_true_is_returned(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    plan_draft = plan_generator.draft_plan()
    approval_response = seek_approval(plan_draft.id)
    assert approval_response.is_approved is True


@injection_test
def test_that_returned_new_plan_id_is_uuid(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    plan_draft = plan_generator.draft_plan()
    approval_response = seek_approval(plan_draft.id)
    assert isinstance(approval_response.new_plan_id, UUID)


@injection_test
def test_that_approval_date_has_correct_day_of_month(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
    datetime_service: FakeDatetimeService,
    plan_repository: PlanRepository,
):
    datetime_service.freeze_time(datetime(year=2021, month=5, day=3))
    draft = plan_generator.draft_plan()
    seek_approval(draft.id)
    new_plan = plan_repository.get_plan_by_id(draft.id)
    assert new_plan
    assert new_plan.approval_date
    assert 3 == new_plan.approval_date.day


@injection_test
def test_that_approved_plan_has_same_planner_as_draft(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
    plan_repository: PlanRepository,
):
    draft = plan_generator.draft_plan()
    seek_approval(draft.id)
    new_plan = plan_repository.get_plan_by_id(draft.id)
    assert new_plan
    assert new_plan.planner == draft.planner
