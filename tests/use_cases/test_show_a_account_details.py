from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from arbeitszeit.use_cases.show_a_account_details import ShowAAccountDetailsUseCase
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    PlanGenerator,
    PurchaseGenerator,
)
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


@injection_test
def test_no_transactions_returned_when_no_transactions_took_place(
    show_a_account_details: ShowAAccountDetailsUseCase,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company_entity()

    response = show_a_account_details(company.id)
    assert not response.transactions


@injection_test
def test_balance_is_zero_when_no_transactions_took_place(
    show_a_account_details: ShowAAccountDetailsUseCase,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company_entity()

    response = show_a_account_details(company.id)
    assert response.account_balance == 0


@injection_test
def test_company_id_is_returned(
    show_p_account_details: ShowAAccountDetailsUseCase,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company_entity()

    response = show_p_account_details(company.id)
    assert response.company_id == company.id


@injection_test
def test_that_no_info_is_generated_after_selling_of_consumer_product(
    show_a_account_details: ShowAAccountDetailsUseCase,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(planner=company)
    response = show_a_account_details(company)
    transactions_before_purchase = len(response.transactions)
    purchase_generator.create_purchase_by_member(plan=plan.id)
    response = show_a_account_details(company)
    assert len(response.transactions) == transactions_before_purchase


@injection_test
def test_that_no_info_is_generated_when_company_sells_p(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    purchase_generator: PurchaseGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(planner=company)
    response = show_a_account_details(company)
    transactions_before_purchase = len(response.transactions)
    purchase_generator.create_fixed_means_purchase(plan=plan.id)
    response = show_a_account_details(company)
    assert len(response.transactions) == transactions_before_purchase


@injection_test
def test_after_approving_a_plan_one_transaction_is_recorded(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company)
    response = show_a_account_details(company)
    assert len(response.transactions) == 1


@injection_test
def test_that_correct_info_is_generated_when_credit_for_wages_is_granted(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(
            labour_cost=Decimal(8.5),
            means_cost=Decimal(0),
            resource_cost=Decimal(0),
        ),
    )
    response = show_a_account_details(company)
    assert len(response.transactions) == 1
    assert response.transactions[0].transaction_volume == Decimal(8.5)
    assert response.transactions[0].purpose is not None
    assert isinstance(response.transactions[0].date, datetime)
    assert (
        response.transactions[0].transaction_type == TransactionTypes.credit_for_wages
    )
    assert response.account_balance == Decimal(8.5)


@injection_test
def test_that_correct_info_is_generated_after_company_transfering_work_certificates(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    register_hours_worked: RegisterHoursWorked,
):
    hours_worked = Decimal("8.5")
    member = member_generator.create_member()
    company = company_generator.create_company(workers=[member])
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=company,
            worker_id=member,
            hours_worked=hours_worked,
        )
    )
    response = show_a_account_details(company)
    transaction = response.transactions[0]
    assert transaction.transaction_type == TransactionTypes.payment_of_wages
    assert transaction.transaction_volume == -hours_worked
    assert response.account_balance == -hours_worked


@injection_test
def test_that_plotting_info_is_empty_when_no_transactions_occurred(
    show_a_account_details: ShowAAccountDetailsUseCase,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company_entity()

    response = show_a_account_details(company.id)
    assert not response.plot.timestamps
    assert not response.plot.accumulated_volumes


@injection_test
def test_that_plotting_info_is_generated_after_transfer_of_work_certificates(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    register_hours_worked: RegisterHoursWorked,
):
    hours_worked = Decimal("8.5")
    worker = member_generator.create_member()
    own_company = company_generator.create_company(workers=[worker])
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=own_company,
            worker_id=worker,
            hours_worked=hours_worked,
        )
    )
    response = show_a_account_details(own_company)
    assert response.plot.timestamps
    assert response.plot.accumulated_volumes


@injection_test
def test_that_correct_plotting_info_is_generated_after_transferring_of_work_certs_to_two_workers(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    register_hours_worked: RegisterHoursWorked,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime(2000, 1, 1))
    worker1 = member_generator.create_member()
    worker2 = member_generator.create_member()
    own_company = company_generator.create_company(workers=[worker1, worker2])
    expected_transaction_1_timestamp = datetime(2000, 1, 2)
    datetime_service.freeze_time(expected_transaction_1_timestamp)
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=own_company,
            worker_id=worker1,
            hours_worked=Decimal("10"),
        )
    )
    expected_transaction_2_timestamp = datetime(2000, 1, 3)
    datetime_service.freeze_time(expected_transaction_2_timestamp)
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=own_company,
            worker_id=worker2,
            hours_worked=Decimal("10"),
        )
    )
    response = show_a_account_details(own_company)
    assert len(response.plot.timestamps) == 2
    assert len(response.plot.accumulated_volumes) == 2

    assert expected_transaction_1_timestamp in response.plot.timestamps
    assert expected_transaction_2_timestamp in response.plot.timestamps

    assert Decimal("-10") in response.plot.accumulated_volumes
    assert Decimal("-20") in response.plot.accumulated_volumes


@injection_test
def test_that_plotting_info_is_generated_in_the_correct_order_after_transfer_of_certs_to_three_workers(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    register_hours_worked: RegisterHoursWorked,
    datetime_service: FakeDatetimeService,
):
    worker1 = member_generator.create_member()
    worker2 = member_generator.create_member()
    worker3 = member_generator.create_member()
    own_company = company_generator.create_company_entity(
        workers=[worker1, worker2, worker3]
    )

    first_transaction_timestamp = datetime(2000, 1, 1)
    datetime_service.freeze_time(first_transaction_timestamp)
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=own_company.id,
            worker_id=worker1,
            hours_worked=Decimal("10"),
        )
    )
    seconds_transaction_timestamp = datetime(2000, 1, 2)
    datetime_service.freeze_time(seconds_transaction_timestamp)
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=own_company.id,
            worker_id=worker2,
            hours_worked=Decimal("10"),
        )
    )
    third_transaction_timestamp = datetime(2000, 1, 3)
    datetime_service.freeze_time(third_transaction_timestamp)
    register_hours_worked(
        RegisterHoursWorkedRequest(
            company_id=own_company.id,
            worker_id=worker3,
            hours_worked=Decimal("10"),
        )
    )

    response = show_a_account_details(own_company.id)
    assert response.plot.timestamps[0] == first_transaction_timestamp
    assert response.plot.timestamps[2] == third_transaction_timestamp

    assert response.plot.accumulated_volumes[0] == Decimal(-10)
    assert response.plot.accumulated_volumes[2] == Decimal(-30)


@injection_test
def test_that_correct_plotting_info_is_generated_after_receiving_of_work_certificates_from_social_accounting(
    show_a_account_details: ShowAAccountDetailsUseCase,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    transaction_timestamp = datetime(2030, 1, 1)
    expected_labour_time = Decimal(123)
    datetime_service.freeze_time(transaction_timestamp)
    company = company_generator.create_company()
    plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(
            labour_cost=expected_labour_time,
            means_cost=Decimal(0),
            resource_cost=Decimal(0),
        ),
    )
    response = show_a_account_details(company)

    assert response.plot.timestamps
    assert response.plot.accumulated_volumes

    assert len(response.plot.timestamps) == 1
    assert len(response.plot.accumulated_volumes) == 1

    assert transaction_timestamp in response.plot.timestamps
    assert expected_labour_time in response.plot.accumulated_volumes
