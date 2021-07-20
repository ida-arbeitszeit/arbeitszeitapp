import pytest
from arbeitszeit.use_cases import pay_means_of_production, PurposesOfPurchases
from tests.repositories import TransactionRepository
from tests.dependency_injection import injection_test
from tests.data_generators import CompanyGenerator, PlanGenerator
from arbeitszeit import errors


@injection_test
def test_assertion_error_is_raised_if_purpose_is_other_than_means_or_raw_materials(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.consumption
    pieces = 5
    with pytest.raises(AssertionError):
        pay_means_of_production(
            transaction_repository, sender, receiver, plan, pieces, purpose
        )


@injection_test
def test_error_is_raised_if_money_is_sent_to_nonexisting_company(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = None
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    with pytest.raises(errors.CompanyDoesNotExist):
        pay_means_of_production(
            transaction_repository, sender, receiver, plan, pieces, purpose
        )


@injection_test
def test_error_is_raised_if_specified_plan_does_not_exist(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = None
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    with pytest.raises(errors.PlanDoesNotExist):
        pay_means_of_production(
            transaction_repository, sender, receiver, plan, pieces, purpose
        )


@injection_test
def test_error_is_raised_if_receiver_is_not_equal_to_planner(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    with pytest.raises(errors.CompanyIsNotPlanner):
        pay_means_of_production(
            transaction_repository, sender, receiver, plan, pieces, purpose
        )


@injection_test
def test_balance_of_buyer_of_means_of_prod_reduced(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5

    pay_means_of_production(
        transaction_repository, sender, receiver, plan, pieces, purpose
    )

    price_total = pieces * (plan.costs_p + plan.costs_r + plan.costs_a)
    assert sender.means_account.balance == -price_total


@injection_test
def test_balance_of_buyer_of_raw_materials_reduced(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        transaction_repository, sender, receiver, plan, pieces, purpose
    )

    price_total = pieces * (plan.costs_p + plan.costs_r + plan.costs_a)
    assert sender.raw_material_account.balance == -price_total


@injection_test
def test_balance_of_seller_increased(
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        transaction_repository, sender, receiver, plan, pieces, purpose
    )

    price_total = pieces * (plan.costs_p + plan.costs_r + plan.costs_a)
    assert receiver.product_account.balance == price_total


# to do: add correct transactions
