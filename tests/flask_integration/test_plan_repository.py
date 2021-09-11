from datetime import datetime

from project.database.repositories import PlanRepository
from arbeitszeit.entities import ProductionCosts

from ..data_generators import PlanGenerator
from ..datetime_service import FakeDatetimeService
from .dependency_injection import injection_test


@injection_test
def test_active_plans_are_counted_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
):
    assert plan_repository.count_active_plans() == 0
    plan_generator.create_plan(activation_date=datetime.min)
    plan_generator.create_plan(activation_date=datetime.min)
    assert plan_repository.count_active_plans() == 2


@injection_test
def test_active_public_plans_are_counted_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
):
    assert plan_repository.count_active_public_plans() == 0
    plan_generator.create_plan(activation_date=datetime.min, is_public_service=True)
    plan_generator.create_plan(activation_date=datetime.min, is_public_service=True)
    plan_generator.create_plan(activation_date=datetime.min, is_public_service=False)
    assert plan_repository.count_active_public_plans() == 2


@injection_test
def test_avg_timeframe_of_active_plans_is_calculated_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
):
    assert plan_repository.avg_timeframe_of_active_plans() == 0
    plan_generator.create_plan(activation_date=datetime.min, timeframe=5)
    plan_generator.create_plan(activation_date=datetime.min, timeframe=3)
    plan_generator.create_plan(activation_date=None, timeframe=20)
    assert plan_repository.avg_timeframe_of_active_plans() == 4


@injection_test
def test_sum_of_active_planned_work_calculated_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
):
    assert plan_repository.sum_of_active_planned_work() == 0
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=ProductionCosts(labour_cost=2, resource_cost=0, means_cost=0),
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=ProductionCosts(labour_cost=3, resource_cost=0, means_cost=0),
    )
    assert plan_repository.sum_of_active_planned_work() == 5


@injection_test
def test_sum_of_active_planned_resources_calculated_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
):
    assert plan_repository.sum_of_active_planned_resources() == 0
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=ProductionCosts(labour_cost=0, resource_cost=2, means_cost=0),
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=ProductionCosts(labour_cost=0, resource_cost=3, means_cost=0),
    )
    assert plan_repository.sum_of_active_planned_resources() == 5


@injection_test
def test_sum_of_active_planned_means_calculated_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
):
    assert plan_repository.sum_of_active_planned_means() == 0
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=ProductionCosts(labour_cost=0, resource_cost=0, means_cost=2),
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=ProductionCosts(labour_cost=0, resource_cost=0, means_cost=3),
    )
    assert plan_repository.sum_of_active_planned_means() == 5


@injection_test
def test_get_approved_plans_created_before_returns_no_plans_by_default(
    repo: PlanRepository,
) -> None:
    plans = list(
        repo.get_approved_plans_created_before(
            datetime.min,
        )
    )
    assert not plans


@injection_test
def test_approved_plans_created_are_not_returned_when_querying_for_datetime_minimum(
    repo: PlanRepository, generator: PlanGenerator
) -> None:
    generator.create_plan(approved=True)
    plans = list(
        repo.get_approved_plans_created_before(
            datetime.min,
        )
    )
    assert not plans


@injection_test
def test_approved_plans_created_are_returned_when_querying_for_datetime_maximum(
    repo: PlanRepository, generator: PlanGenerator
) -> None:
    generator.create_plan(approved=True)
    plans = list(
        repo.get_approved_plans_created_before(
            datetime.max,
        )
    )
    assert len(plans) == 1


@injection_test
def test_when_querying_for_plans_created_before_date_then_plans_created_after_that_date_are_not_returned(
    repo: PlanRepository,
    generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
) -> None:
    datetime_service.freeze_time(datetime(year=2020, month=1, day=1))
    first_plan = generator.create_plan(approved=True)
    datetime_service.freeze_time(datetime(year=2021, month=1, day=1))
    plans = list(
        repo.get_approved_plans_created_before(
            datetime(year=2020, month=12, day=31),
        )
    )
    assert len(plans) == 1
    assert plans[0].id == first_plan.id
