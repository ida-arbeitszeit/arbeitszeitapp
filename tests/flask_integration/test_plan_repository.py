from datetime import datetime
from decimal import Decimal
from typing import Union
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from project.database.repositories import PlanRepository

from ..data_generators import CompanyGenerator, PlanGenerator
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


@injection_test
def test_get_plan_by_id_with_unnkown_id_results_in_none(
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
def test_that_all_plan_for_a_company_are_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company)
    plan_generator.create_plan(approved=True, planner=company)
    plan_generator.create_plan(
        approved=True, activation_date=datetime.now(), planner=company
    )
    returned_plans = list(repository.get_all_plans_for_company(company_id=company.id))
    assert len(returned_plans) == 3


@injection_test
def test_that_approved_non_active_plan_for_company_is_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    expected_plan = plan_generator.create_plan(approved=True, planner=company)
    returned_plan = list(
        repository.get_non_active_plans_for_company(company_id=company.id)
    )[0]
    assert (
        expected_plan.id == returned_plan.id
        and returned_plan.approved
        and not returned_plan.is_active
        and not returned_plan.expired
    )


@injection_test
def test_that_approved_and_active_plan_for_company_is_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    expected_plan = plan_generator.create_plan(
        approved=True, activation_date=datetime.now(), planner=company
    )
    returned_plan = list(
        repository.get_active_plans_for_company(company_id=company.id)
    )[0]
    assert (
        expected_plan.id == returned_plan.id
        and returned_plan.approved
        and returned_plan.is_active
        and not returned_plan.expired
    )


@injection_test
def test_that_expired_plan_for_company_is_returned(
    repository: PlanRepository,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    expected_plan = plan_generator.create_plan(expired=True, planner=company)
    returned_plan = list(
        repository.get_expired_plans_for_company(company_id=company.id)
    )[0]
    assert expected_plan.id == returned_plan.id and returned_plan.expired


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
