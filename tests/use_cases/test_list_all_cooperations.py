from datetime import datetime, timedelta
from uuid import UUID

from arbeitszeit.use_cases.list_all_cooperations import (
    ListAllCooperations,
    ListAllCooperationsResponse,
)
from tests.data_generators import CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


def coop_in_response(cooperation: UUID, response: ListAllCooperationsResponse) -> bool:
    return any(cooperation == result.id for result in response.cooperations)


@injection_test
def test_empty_list_is_returned_when_there_are_no_cooperations(
    use_case: ListAllCooperations,
):
    response = use_case()
    assert len(response.cooperations) == 0


@injection_test
def test_one_empty_cooperation_is_returned_if_there_is_one_coop_without_plans(
    use_case: ListAllCooperations, cooperation_generator: CooperationGenerator
):
    cooperation = cooperation_generator.create_cooperation()
    response = use_case()
    assert len(response.cooperations) == 1
    assert response.cooperations[0].plan_count == 0
    assert coop_in_response(cooperation, response)


@injection_test
def test_one_returned_cooperation_shows_correct_info(
    use_case: ListAllCooperations,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
):
    expected_cooperation_name = "Test Cooperation"
    plan = plan_generator.create_plan()
    cooperation = cooperation_generator.create_cooperation(
        plans=[plan], name=expected_cooperation_name
    )
    response = use_case()
    assert len(response.cooperations) == 1
    assert coop_in_response(cooperation, response)
    assert response.cooperations[0].plan_count == 1
    assert response.cooperations[0].id == cooperation
    assert response.cooperations[0].name == expected_cooperation_name


@injection_test
def test_one_cooperation_with_correct_plan_count_is_returned_if_there_is_one_coop_with_2_plans(
    use_case: ListAllCooperations,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
) -> None:
    plan1 = plan_generator.create_plan()
    plan2 = plan_generator.create_plan()
    cooperation = cooperation_generator.create_cooperation(plans=[plan1, plan2])
    response = use_case()
    assert response.cooperations[0].plan_count == 2
    assert coop_in_response(cooperation, response)


@injection_test
def test_that_expired_plans_are_not_included_in_plan_count(
    use_case: ListAllCooperations,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
) -> None:
    datetime_service.freeze_time(datetime(2000, 1, 1))
    plan = plan_generator.create_plan(timeframe=1)
    cooperation_generator.create_cooperation(plans=[plan])
    datetime_service.advance_time(timedelta(days=2))
    response = use_case()
    assert response.cooperations[0].plan_count == 0
