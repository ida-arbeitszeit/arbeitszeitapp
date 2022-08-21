from decimal import Decimal
from typing import Union

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import GetStatistics
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.data_generators import (
    CompanyGenerator,
    CooperationGenerator,
    MemberGenerator,
    PlanGenerator,
    TransactionGenerator,
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
def test_counting_of_cooperations(
    get_statistics: GetStatistics, coop_generator: CooperationGenerator
):
    number_of_coops = 2
    for _ in range(number_of_coops):
        coop_generator.create_cooperation()
    stats = get_statistics()
    assert stats.cooperations_count == number_of_coops


@injection_test
def test_counting_of_certificates_when_certs_are_zero(
    get_statistics: GetStatistics,
):
    stats = get_statistics()
    assert stats.certificates_count == 0


@injection_test
def test_counting_of_certificates_when_two_members_have_received_certs(
    get_statistics: GetStatistics,
    member_generator: MemberGenerator,
    transaction_generator: TransactionGenerator,
):
    num_transactions = 2
    for _ in range(num_transactions):
        worker = member_generator.create_member()
        account = worker.account
        transaction_generator.create_transaction(
            receiving_account=account,
            amount_received=Decimal(10),
        )
    stats = get_statistics()
    assert stats.certificates_count == num_transactions * Decimal(10)


@injection_test
def test_counting_of_certificates_when_one_worker_and_one_company_have_received_certs(
    get_statistics: GetStatistics,
    member_generator: MemberGenerator,
    transaction_generator: TransactionGenerator,
    company_generator: CompanyGenerator,
):
    # worker receives certs
    worker = member_generator.create_member()
    worker_account = worker.account
    transaction_generator.create_transaction(
        receiving_account=worker_account,
        amount_received=Decimal(10.5),
    )
    # company receives certs
    company = company_generator.create_company()
    company_account = company.work_account
    transaction_generator.create_transaction(
        receiving_account=company_account, amount_received=Decimal(10)
    )
    stats = get_statistics()
    assert stats.certificates_count == Decimal(20.5)


@injection_test
def test_available_product_is_positive_number_when_amount_on_prd_account_is_negative(
    get_statistics: GetStatistics,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    transaction_generator.create_transaction(
        receiving_account=company.product_account, amount_received=Decimal(-10)
    )
    stats = get_statistics()
    assert stats.available_product == Decimal(10)


@injection_test
def test_correct_available_product_is_shown_when_two_companies_have_received_prd_debit(
    get_statistics: GetStatistics,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    num_companies = 2
    for _ in range(num_companies):
        company = company_generator.create_company()
        transaction_generator.create_transaction(
            receiving_account=company.product_account, amount_received=Decimal(-22)
        )
    stats = get_statistics()
    assert stats.available_product == num_companies * Decimal(22)


@injection_test
def test_counting_of_active_plans(
    get_statistics: GetStatistics,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
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
def test_that_use_case_returns_none_for_current_payout_factor_if_it_never_has_been_calculated(
    get_statistics: GetStatistics,
):
    stats = get_statistics()
    assert stats.payout_factor is None


@injection_test
def test_that_use_case_shows_the_current_payout_factor_if_it_has_been_calculated(
    get_statistics: GetStatistics, update_plans_and_payout: UpdatePlansAndPayout
):
    update_plans_and_payout()
    stats = get_statistics()
    assert stats.payout_factor is not None
