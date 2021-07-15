import pytest

from arbeitszeit.transaction_factory import TransactionFactory
from arbeitszeit.use_cases import grant_credit
from arbeitszeit.entities import AccountTypes
from tests.repositories import TransactionRepository

from .data_generators import PlanGenerator, SocialAccountingGenerator
from .dependency_injection import injection_test


@injection_test
def test_that_assertion_error_is_raised_if_plan_has_not_been_approved(
    plan_generator: PlanGenerator,
    social_accounting_generator: SocialAccountingGenerator,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):
    plan = plan_generator.create_plan(approved=False)
    social_accounting = social_accounting_generator.create_social_accounting()
    with pytest.raises(AssertionError):
        grant_credit(
            plan,
            social_accounting,
            transaction_repository,
            transaction_factory,
        )


@injection_test
def test_account_balances_adjusted(
    plan_generator: PlanGenerator,
    social_accounting_generator: SocialAccountingGenerator,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):
    plan = plan_generator.create_plan(approved=True)
    social_accounting = social_accounting_generator.create_social_accounting()
    grant_credit(
        plan,
        social_accounting,
        transaction_repository,
        transaction_factory,
    )
    assert plan.planner.means_account.balance == plan.costs_p
    assert plan.planner.raw_material_account.balance == plan.costs_r
    assert plan.planner.work_account.balance == plan.costs_a
    assert plan.planner.product_account.balance == -(
        plan.costs_p + plan.costs_r + plan.costs_a
    )


@injection_test
def test_that_all_transactions_have_accounting_as_sender(
    plan_generator: PlanGenerator,
    social_accounting_generator: SocialAccountingGenerator,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):
    plan = plan_generator.create_plan(approved=True)
    social_accounting = social_accounting_generator.create_social_accounting()
    grant_credit(
        plan,
        social_accounting,
        transaction_repository,
        transaction_factory,
    )
    for transaction in transaction_repository.transactions:
        assert transaction.account_from.account_type == AccountTypes.accounting


@injection_test
def test_that_transactions_with_all_four_account_types_as_receivers_are_added_to_repo(
    plan_generator: PlanGenerator,
    social_accounting_generator: SocialAccountingGenerator,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):
    plan = plan_generator.create_plan(approved=True)
    social_accounting = social_accounting_generator.create_social_accounting()
    grant_credit(
        plan,
        social_accounting,
        transaction_repository,
        transaction_factory,
    )
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
    plan_generator: PlanGenerator,
    social_accounting_generator: SocialAccountingGenerator,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):
    plan = plan_generator.create_plan(approved=True)
    expected_amount_p, expected_amount_r, expected_amount_a, expected_amount_prd = (
        plan.costs_p,
        plan.costs_r,
        plan.costs_a,
        -(plan.costs_p + plan.costs_r + plan.costs_a),
    )
    social_accounting = social_accounting_generator.create_social_accounting()
    grant_credit(
        plan,
        social_accounting,
        transaction_repository,
        transaction_factory,
    )
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
