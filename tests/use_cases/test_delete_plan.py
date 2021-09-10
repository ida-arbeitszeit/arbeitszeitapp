from typing import Dict, Optional
from uuid import UUID

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases import DeletePlan
from tests.data_generators import PlanGenerator

from ..datetime_service import FakeDatetimeService
from .dependency_injection import injection_test
from .repositories import PlanRepository


def plan_in_plans(plan: Plan, plans: Dict[UUID, Plan]) -> Optional[Plan]:
    return plans.get(plan.id)


@injection_test
def test_that_active_plan_does_not_get_deleted(
    plan_repo: PlanRepository,
    delete_plan: DeletePlan,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )

    delete_plan(plan.id)
    assert len(plan_repo.plans) == 1


@injection_test
def test_that_plan_gets_deleted(
    plan_repo: PlanRepository,
    delete_plan: DeletePlan,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    delete_plan(plan.id)
    assert len(plan_repo.plans) == 0


@injection_test
def test_that_correct_plan_gets_deleted(
    plan_repo: PlanRepository,
    delete_plan: DeletePlan,
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan()
    plan2 = plan_generator.create_plan()
    plan3 = plan_generator.create_plan()
    delete_plan(plan2.id)
    assert plan_in_plans(plan1, plan_repo.plans)
    assert not plan_in_plans(plan2, plan_repo.plans)
    assert plan_in_plans(plan3, plan_repo.plans)


@injection_test
def test_that_correct_response_gets_returned_for_inactive_plan(
    delete_plan: DeletePlan,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    response = delete_plan(plan.id)
    assert response.plan_id == plan.id
    assert response.is_success == True


@injection_test
def test_that_correct_response_gets_returned_for_active_plan(
    delete_plan: DeletePlan,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    response = delete_plan(plan.id)
    assert response.plan_id == plan.id
    assert response.is_success == False
