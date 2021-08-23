from arbeitszeit.use_cases import GetStatistics
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import injection_test


@injection_test
def test_that_counts_are_zero_if_repositories_are_empty(get_statistics: GetStatistics):
    stats = get_statistics()
    assert stats.registered_companies_count == 0
    assert stats.registered_members_count == 0
    assert stats.active_plans_count == 0
    assert stats.active_plans_public_count == 0


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
