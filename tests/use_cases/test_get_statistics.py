from decimal import Decimal
from typing import Union
from datetime import datetime

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import GetStatistics
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    OfferGenerator,
    PlanGenerator,
)
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test

Number = Union[int, Decimal]


def production_costs(p: Number, r: Number, a: Number) -> ProductionCosts:
    return ProductionCosts(
        Decimal(p),
        Decimal(r),
        Decimal(a),
    )


@injection_test
def test_that_values_are_zero_if_repositories_are_empty(get_statistics: GetStatistics):
    stats = get_statistics()
    assert stats.registered_companies_count == 0
    assert stats.registered_members_count == 0
    assert stats.active_plans_count == 0
    assert stats.active_plans_public_count == 0
    assert stats.avg_timeframe == 0
    assert stats.planned_work == 0
    assert stats.planned_resources == 0
    assert stats.planned_means == 0
    assert stats.products_on_marketplace_count == 0


@injection_test
def test_counting_of_companies(
    get_statistics: GetStatistics, company_generator: CompanyGenerator
):
    company_generator.create_company()
    company_generator.create_company()
    stats = get_statistics()
    assert stats.registered_companies_count == 2


@injection_test
def test_counting_of_members(
    get_statistics: GetStatistics, member_generator: MemberGenerator
):
    member_generator.create_member()
    member_generator.create_member()
    stats = get_statistics()
    assert stats.registered_members_count == 2


@injection_test
def test_counting_of_active_plans(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None)
    plan_generator.create_plan(activation_date=datetime_service.now_minus_one_day())
    plan_generator.create_plan(activation_date=datetime_service.now_minus_one_day())
    stats = get_statistics()
    assert stats.active_plans_count == 2


@injection_test
def test_counting_of_plans_that_are_both_active_and_public(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    stats = get_statistics()
    assert stats.active_plans_public_count == 2


@injection_test
def test_that_inactive_and_productive_plans_are_ignored_when_counting_active_and_public_plans(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, is_public_service=True)
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=False
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    stats = get_statistics()
    assert stats.active_plans_public_count == 1


@injection_test
def test_average_calculation_of_two_active_plan_timeframes(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=7
    )
    stats = get_statistics()
    assert stats.avg_timeframe == 5


@injection_test
def test_that_inactive_plans_are_ignored_when_calculating_average_of_plan_timeframes(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, timeframe=20)
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    stats = get_statistics()
    assert stats.avg_timeframe == 3


@injection_test
def test_adding_up_work_of_two_plans(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(3, 1, 1),
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(2, 1, 1),
    )
    stats = get_statistics()
    assert stats.planned_work == 5


@injection_test
def test_that_inactive_plans_are_ignored_when_adding_up_work(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, costs=production_costs(10, 1, 1))
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(3, 1, 1),
    )
    stats = get_statistics()
    assert stats.planned_work == 3


@injection_test
def test_adding_up_resources_of_two_plans(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(1, 3, 1),
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(1, 2, 1),
    )
    stats = get_statistics()
    assert stats.planned_resources == 5


@injection_test
def test_that_inactive_plans_are_ignored_when_adding_up_resources(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, costs=production_costs(1, 10, 1))
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(1, 3, 1),
    )
    stats = get_statistics()
    assert stats.planned_resources == 3


@injection_test
def test_adding_up_means_of_two_plans(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(1, 1, 3),
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(1, 1, 2),
    )
    stats = get_statistics()
    assert stats.planned_means == 5


@injection_test
def test_that_inactive_plans_are_ignored_when_adding_up_means(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, costs=production_costs(1, 1, 10))
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=production_costs(1, 1, 3),
    )
    stats = get_statistics()
    assert stats.planned_means == 3


@injection_test
def test_counting_of_marketplace_products(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
):
    offer_generator.create_offer(
        plan=plan_generator.create_plan(activation_date=datetime.min)
    )
    offer_generator.create_offer(
        plan=plan_generator.create_plan(activation_date=datetime.min)
    )
    stats = get_statistics()
    assert stats.products_on_marketplace_count == 2


@injection_test
def test_that_plan_duplicates_are_ignored_when_counting_marketplace_products(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer_generator.create_offer(plan=plan)
    offer_generator.create_offer(plan=plan)
    stats = get_statistics()
    assert stats.products_on_marketplace_count == 1
