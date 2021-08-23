from arbeitszeit.use_cases import GetStatistics
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    PlanGenerator,
    OfferGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import injection_test
from arbeitszeit.entities import ProductionCosts


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
def test_that_correct_company_count_is_shown(
    get_statistics: GetStatistics, company_generator: CompanyGenerator
):
    company_generator.create_company()
    company_generator.create_company()
    stats = get_statistics()
    assert stats.registered_companies_count == 2


@injection_test
def test_that_correct_member_count_is_shown(
    get_statistics: GetStatistics, member_generator: MemberGenerator
):
    member_generator.create_member()
    member_generator.create_member()
    stats = get_statistics()
    assert stats.registered_members_count == 2


@injection_test
def test_that_correct_active_plan_count_is_shown(
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
def test_that_correct_active_and_public_plan_count_is_shown(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, is_public_service=True)
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), is_public_service=True
    )
    stats = get_statistics()
    assert stats.active_plans_public_count == 2


@injection_test
def test_that_correct_avg_plan_timeframe_is_shown(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, timeframe=20)
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=7
    )
    stats = get_statistics()
    assert stats.avg_timeframe == 5


@injection_test
def test_that_correct_sum_of_planned_work_is_shown(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, costs=ProductionCosts(10, 1, 1))
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(3, 1, 1),
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(2, 1, 1),
    )
    stats = get_statistics()
    assert stats.planned_work == 5


@injection_test
def test_that_correct_sum_of_planned_resources_is_shown(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, costs=ProductionCosts(10, 1, 1))
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(1, 3, 1),
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(1, 2, 1),
    )
    stats = get_statistics()
    assert stats.planned_resources == 5


@injection_test
def test_that_correct_sum_of_planned_means_is_shown(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    plan_generator.create_plan(activation_date=None, costs=ProductionCosts(10, 1, 1))
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(1, 1, 3),
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(1, 1, 2),
    )
    stats = get_statistics()
    assert stats.planned_means == 5


@injection_test
def test_that_correct_products_on_marketplace_count_is_shown_and_plan_duplicates_ignored(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
):
    plan1 = plan_generator.create_plan()
    offer_generator.create_offer(plan=plan1)
    offer_generator.create_offer(plan=plan1)
    plan2 = plan_generator.create_plan()
    offer_generator.create_offer(plan=plan2)
    stats = get_statistics()
    assert stats.products_on_marketplace_count == 2
