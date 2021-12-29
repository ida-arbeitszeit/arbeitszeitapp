from datetime import datetime

from arbeitszeit.entities import Cooperation
from arbeitszeit.use_cases import ListAllCooperations, ListAllCooperationsResponse
from tests.data_generators import CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


def coop_in_response(
    cooperation: Cooperation, response: ListAllCooperationsResponse
) -> bool:
    return any(
        (
            cooperation.id == result.id and cooperation.name == result.name
            for result in response.cooperations
        )
    )


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
    plan = plan_generator.create_plan(activation_date=datetime.min)
    cooperation = cooperation_generator.create_cooperation(plans=[plan])
    response = use_case()
    assert len(response.cooperations) == 1
    assert coop_in_response(cooperation, response)
    assert response.cooperations[0].plan_count == 1
    assert response.cooperations[0].id == cooperation.id
    assert response.cooperations[0].name == cooperation.name


@injection_test
def test_one_cooperation_with_correct_plan_count_is_returned_if_there_is_one_coop_with_2_plans(
    use_case: ListAllCooperations,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan(activation_date=datetime.min)
    plan2 = plan_generator.create_plan(activation_date=datetime.min)
    cooperation = cooperation_generator.create_cooperation(plans=[plan1, plan2])
    response = use_case()
    assert response.cooperations[0].plan_count == 2
    assert coop_in_response(cooperation, response)
