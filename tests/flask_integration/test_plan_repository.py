from project.database.repositories import PlanRepository
from tests.data_generators import PlanGenerator

from .dependency_injection import injection_test
from tests.datetime_service import FakeDatetimeService

# test statistics


@injection_test
def test_active_plans_are_counted_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    assert plan_repository.count_active_plans() == 0
    plan_generator.create_plan(activation_date=datetime_service.now_minus_one_day())
    plan_generator.create_plan(activation_date=datetime_service.now_minus_one_day())
    assert plan_repository.count_active_plans() == 2


@injection_test
def test_active_public_plans_are_counted_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    assert plan_repository.count_active_public_plans() == 0
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=False
    )
    assert plan_repository.count_active_public_plans() == 2


@injection_test
def test_avg_timeframe_of_active_plans_is_calculated_correctly(
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    assert plan_repository.avg_timeframe_of_active_plans() == 0
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=5
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    plan_generator.create_plan(activation_date=None, timeframe=20)
    assert plan_repository.avg_timeframe_of_active_plans() == 4
