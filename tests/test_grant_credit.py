import pytest
from .dependency_injection import injection_test
from arbeitszeit.use_cases import grant_credit
from arbeitszeit.transaction_factory import TransactionFactory
from .data_generators import PlanGenerator, SocialAccountingGenerator
from tests.repositories import TransactionRepository


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


# to do: test correct transactions added
