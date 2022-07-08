from datetime import datetime
from decimal import Decimal
from typing import Union
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit_flask.database.repositories import PlanRepository
from tests.datetime_service import FakeDatetimeService

from ..data_generators import CompanyGenerator, PlanGenerator
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
def test_all_active_plans_get_retrieved(
    repository: PlanRepository,
    generator: PlanGenerator,
) -> None:
    number_of_plans = 5
    list_of_plans = [
        generator.create_plan(activation_date=datetime.min)
        for _ in range(number_of_plans)
    ]
    retrieved_plans = list(repository.get_active_plans())
    assert len(retrieved_plans) == number_of_plans
    for plan in list_of_plans:
        assert plan in retrieved_plans


@injection_test
def test_three_active_plans_get_retrieved_ordered_by_activation_date(
    repository: PlanRepository,
    generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
) -> None:
    activation_dates = [
        datetime_service.now_minus_ten_days(),
        datetime_service.now(),
        datetime_service.now_minus_20_hours(),
        datetime_service.now_minus_25_hours(),
        datetime_service.now_minus_one_day(),
    ]
    plans = [generator.create_plan(activation_date=date) for date in activation_dates]
    retrieved_plans = list(
        repository.get_three_latest_active_plans_ordered_by_activation_date()
    )
    assert len(retrieved_plans) == 3
    assert retrieved_plans[0] == plans[1]
    assert retrieved_plans[1] == plans[2]
    assert retrieved_plans[2] == plans[4]


@injection_test
def test_plans_that_were_set_to_expired_dont_show_up_in_active_plans(
    repository: PlanRepository,
    generator: PlanGenerator,
) -> None:
    plan = generator.create_plan(activation_date=datetime.min)
    assert plan in list(repository.get_active_plans())
    repository.set_plan_as_expired(plan)
    assert plan not in list(repository.get_active_plans())


@injection_test
def test_get_plan_by_id_with_unkown_id_results_in_none(
    repository: PlanRepository,
) -> None:
    assert repository.get_plan_by_id(uuid4()) is None


@injection_test
def test_that_existing_plan_can_be_retrieved_by_id(
    repository: PlanRepository,
    generator: PlanGenerator,
) -> None:
    expected_plan = generator.create_plan()
    assert expected_plan == repository.get_plan_by_id(expected_plan.id)


@injection_test
def test_that_all_plans_for_a_company_are_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company, activation_date=None)
    plan_generator.create_plan(planner=company, is_public_service=True)
    plan_generator.create_plan(planner=company, is_available=False)
    returned_plans = list(
        repository.get_all_plans_for_company_descending(company_id=company.id)
    )
    assert len(returned_plans) == 3


@injection_test
def test_that_all_plans_for_a_company_are_returned_in_descending_order(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
    datetime_service: FakeDatetimeService,
) -> None:
    company = company_generator.create_company()
    third = plan_generator.create_plan(
        planner=company,
        plan_creation_date=datetime_service.now_minus_one_day(),
    )
    second = plan_generator.create_plan(
        planner=company,
        plan_creation_date=datetime_service.now_minus_two_days(),
    )
    first = plan_generator.create_plan(
        planner=company,
        plan_creation_date=datetime_service.now_minus_ten_days(),
    )
    returned_plans = list(
        repository.get_all_plans_for_company_descending(company_id=company.id)
    )
    assert returned_plans[0] == third
    assert returned_plans[1] == second
    assert returned_plans[2] == first


@injection_test
def test_that_all_active_plan_for_a_company_are_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company, activation_date=datetime.min)
    plan_generator.create_plan(planner=company, activation_date=datetime.min)
    plan_generator.create_plan(planner=company)
    returned_plans = list(
        repository.get_all_active_plans_for_company(company_id=company.id)
    )
    assert len(returned_plans) == 2


@injection_test
def test_that_plan_gets_hidden(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan()
    repository.hide_plan(plan.id)
    plan_from_repo = repository.get_plan_by_id(plan.id)
    assert plan_from_repo
    assert plan_from_repo.hidden_by_user


@injection_test
def test_that_query_active_plans_by_exact_product_name_returns_plan(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    expected_plan = plan_generator.create_plan(
        activation_date=datetime.min, product_name="Delivery of goods"
    )
    returned_plan = list(
        repository.query_active_plans_by_product_name("Delivery of goods")
    )
    assert returned_plan
    assert returned_plan[0] == expected_plan


@injection_test
def test_that_query_active_plans_by_substring_of_product_name_returns_plan(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    expected_plan = plan_generator.create_plan(
        activation_date=datetime.min, product_name="Delivery of goods"
    )
    returned_plan = list(repository.query_active_plans_by_product_name("very of go"))
    assert returned_plan
    assert returned_plan[0] == expected_plan


@injection_test
def test_that_query_active_plans_by_substring_of_plan_id_returns_plan(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    expected_plan = plan_generator.create_plan(activation_date=datetime.min)
    expected_plan_id = expected_plan.id
    query = str(expected_plan_id)[3:8]
    returned_plan = list(repository.query_active_plans_by_plan_id(query))
    assert returned_plan
    assert returned_plan[0] == expected_plan


@injection_test
def test_that_active_days_are_set(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan(activation_date=datetime.min)
    assert plan.active_days is None
    repository.set_active_days(plan, 3)
    plan_from_repo = repository.get_plan_by_id(plan.id)
    assert plan_from_repo
    assert plan_from_repo.active_days == 3


@injection_test
def test_that_payout_count_is_increased_by_one(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan(activation_date=datetime.min)
    assert plan.payout_count == 0
    repository.increase_payout_count_by_one(plan)
    plan_from_repo = repository.get_plan_by_id(plan.id)
    assert plan_from_repo
    assert plan_from_repo.payout_count == 1


@injection_test
def test_that_availability_is_toggled_to_false(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan()
    assert plan.is_available == True
    repository.toggle_product_availability(plan)
    plan_from_repo = repository.get_plan_by_id(plan.id)
    assert plan_from_repo
    assert plan_from_repo.is_available == False


@injection_test
def test_that_availability_is_toggled_to_true(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan(is_available=False)
    assert plan.is_available == False
    repository.toggle_product_availability(plan)
    plan_from_repo = repository.get_plan_by_id(plan.id)
    assert plan_from_repo
    assert plan_from_repo.is_available == True


@injection_test
def test_that_all_productive_plans_approved_active_and_not_expired_returns_no_plans_with_empty_db(
    repository: PlanRepository,
) -> None:
    assert not list(repository.all_productive_plans_approved_active_and_not_expired())


@injection_test
def test_all_public_plans_approved_active_and_not_expired_returns_no_plans_with_empty_db(
    repository: PlanRepository,
) -> None:
    assert not list(repository.all_public_plans_approved_active_and_not_expired())


@injection_test
def test_all_plans_approved_active_and_not_expired_returns_no_plans_with_empty_db(
    repository: PlanRepository,
) -> None:
    assert not list(repository.all_plans_approved_active_and_not_expired())


@injection_test
def test_correct_name_and_description_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    expected_name = "name 20220621"
    expected_description = "description 20220621"
    plan = plan_generator.create_plan(
        product_name=expected_name, description=expected_description
    )
    plan_info = repository.get_plan_name_and_description(plan.id)
    assert plan_info.name == expected_name
    assert plan_info.description == expected_description


@injection_test
def test_that_non_existing_plan_returns_no_planner_id(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    plan_generator.create_plan()
    nothing = repository.get_planner_id(uuid4())
    assert nothing is None


@injection_test
def test_that_correct_id_of_planning_company_gets_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
) -> None:
    expected_plan = plan_generator.create_plan()
    plan_id = repository.get_planner_id(expected_plan.id)
    assert plan_id == expected_plan.planner.id
