import pytest

from arbeitszeit import errors
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases import PayMeansOfProduction
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.dependency_injection import injection_test
from tests.repositories import TransactionRepository


@injection_test
def test_assertion_error_is_raised_if_purpose_is_other_than_means_or_raw_materials(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.consumption
    pieces = 5
    with pytest.raises(AssertionError):
        pay_means_of_production(sender, receiver, plan, pieces, purpose)


@injection_test
def test_error_is_raised_if_receiver_is_not_equal_to_planner(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    with pytest.raises(errors.CompanyIsNotPlanner):
        pay_means_of_production(sender, receiver, plan, pieces, purpose)


@injection_test
def test_balance_of_buyer_of_means_of_prod_reduced(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5

    pay_means_of_production(sender, receiver, plan, pieces, purpose)

    price_total = pieces * plan.production_costs.total_cost()
    assert sender.means_account.balance == -price_total


@injection_test
def test_balance_of_buyer_of_raw_materials_reduced(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(sender, receiver, plan, pieces, purpose)

    price_total = pieces * plan.production_costs.total_cost()
    assert sender.raw_material_account.balance == -price_total


@injection_test
def test_balance_of_seller_increased(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(sender, receiver, plan, pieces, purpose)

    price_total = pieces * plan.production_costs.total_cost()
    assert receiver.product_account.balance == price_total


@injection_test
def test_correct_transaction_added_if_means_of_production_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    pay_means_of_production(sender, receiver, plan, pieces, purpose)
    price_total = pieces * plan.production_costs.total_cost()
    assert len(transaction_repository.transactions) == 1
    assert transaction_repository.transactions[0].account_from == sender.means_account
    assert (
        transaction_repository.transactions[0].account_to
        == plan.planner.product_account
    )
    assert transaction_repository.transactions[0].amount == price_total


@injection_test
def test_correct_transaction_added_if_raw_materials_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5
    pay_means_of_production(sender, receiver, plan, pieces, purpose)
    price_total = pieces * plan.production_costs.total_cost()
    assert len(transaction_repository.transactions) == 1
    assert (
        transaction_repository.transactions[0].account_from
        == sender.raw_material_account
    )
    assert (
        transaction_repository.transactions[0].account_to
        == plan.planner.product_account
    )
    assert transaction_repository.transactions[0].amount == price_total
