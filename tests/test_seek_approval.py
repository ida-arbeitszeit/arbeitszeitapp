from datetime import datetime

from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases import SeekApproval
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import injection_test
from tests.repositories import TransactionRepository


@injection_test
def test_that_any_plan_will_be_approved(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    seek_approval(new_plan, original_plan)
    assert new_plan.approved


@injection_test
def test_that_any_plan_will_be_approved_and_original_plan_renewed(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    seek_approval(new_plan, original_plan)
    assert new_plan.approved
    assert original_plan.renewed


@injection_test
def test_that_true_is_returned(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    is_approval = seek_approval(new_plan, original_plan)
    assert is_approval is True


@injection_test
def test_that_approval_date_has_correct_day_of_month(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime(year=2021, month=5, day=3))
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    seek_approval(new_plan, original_plan)
    assert new_plan.approval_date
    assert 3 == new_plan.approval_date.day


@injection_test
def test_account_balances_adjusted(
    seek_approval: SeekApproval,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    seek_approval(plan, None)
    assert plan.planner.means_account.balance == plan.production_costs.means_cost
    assert (
        plan.planner.raw_material_account.balance == plan.production_costs.resource_cost
    )
    assert plan.planner.work_account.balance == plan.production_costs.labour_cost
    assert plan.planner.product_account.balance == -(plan.production_costs.total_cost())


@injection_test
def test_that_all_transactions_have_accounting_as_sender(
    seek_approval: SeekApproval,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan()
    seek_approval(plan, None)
    for transaction in transaction_repository.transactions:
        assert transaction.account_from.account_type == AccountTypes.accounting


@injection_test
def test_that_transactions_with_all_four_account_types_as_receivers_are_added_to_repo(
    seek_approval: SeekApproval,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan()
    seek_approval(plan, None)
    added_account_types = [
        transaction.account_to.account_type
        for transaction in transaction_repository.transactions
    ]
    for account_type in (
        AccountTypes.p,
        AccountTypes.r,
        AccountTypes.a,
        AccountTypes.prd,
    ):
        assert account_type in added_account_types


@injection_test
def test_that_added_transactions_have_correct_amounts(
    seek_approval: SeekApproval,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan()
    expected_amount_p, expected_amount_r, expected_amount_a, expected_amount_prd = (
        plan.production_costs.means_cost,
        plan.production_costs.resource_cost,
        plan.production_costs.labour_cost,
        -plan.production_costs.total_cost(),
    )
    seek_approval(plan, None)
    for trans in transaction_repository.transactions:
        if trans.account_to.account_type == AccountTypes.p:
            added_amount_p = trans.amount
        elif trans.account_to.account_type == AccountTypes.r:
            added_amount_r = trans.amount
        elif trans.account_to.account_type == AccountTypes.a:
            added_amount_a = trans.amount
        elif trans.account_to.account_type == AccountTypes.prd:
            added_amount_prd = trans.amount

    assert expected_amount_p == added_amount_p
    assert expected_amount_r == added_amount_r
    assert expected_amount_a == added_amount_a
    assert expected_amount_prd == added_amount_prd
