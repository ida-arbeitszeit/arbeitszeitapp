from datetime import datetime
from decimal import Decimal
from typing import Union

from arbeitszeit.entities import ProductionCosts
from project.database.repositories import PlanRepository

from ..data_generators import PlanGenerator
from ..datetime_service import FakeDatetimeService
from .dependency_injection import injection_test

Number = Union[int, Decimal]


def production_costs(a: Number, r: Number, p: Number) -> ProductionCosts:
    return ProductionCosts(
        Decimal(a),
        Decimal(r),
        Decimal(p),
    )


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
        costs=production_costs(2, 0, 0),
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=production_costs(3, 0, 0),
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
        costs=production_costs(0, 2, 0),
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=production_costs(0, 3, 0),
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
        costs=production_costs(0, 0, 2),
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        costs=production_costs(0, 0, 3),
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


@injection_test
def test_plans_that_were_set_to_expired_dont_show_up_in_active_plans(
    repository: PlanRepository,
    generator: PlanGenerator,
) -> None:
    plan = generator.create_plan()
    repository.activate_plan(plan, datetime.now())
    assert plan in list(repository.all_active_plans())
    repository.set_plan_as_expired(plan)
    assert plan not in list(repository.all_active_plans())
