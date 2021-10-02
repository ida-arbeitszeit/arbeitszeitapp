from datetime import datetime
from uuid import uuid4

import pytest

from arbeitszeit import errors
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases import PayMeansOfProduction, PayMeansOfProductionRequest
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test
from .repositories import AccountRepository, PurchaseRepository, TransactionRepository


@injection_test
def test_error_is_raised_if_plan_is_not_active_yet(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    with pytest.raises(errors.PlanIsInactive):
        pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )


@injection_test
def test_error_is_raised_if_plan_is_expired(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        plan_creation_date=datetime_service.now_minus_ten_days(), timeframe=1
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    plan.expired = True
    with pytest.raises(errors.PlanIsInactive):
        pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )


@injection_test
def test_assertion_error_is_raised_if_purpose_is_other_than_means_or_raw_materials(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.consumption
    pieces = 5
    with pytest.raises(AssertionError):
        pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )


@injection_test
def test_error_is_raised_if_trying_to_pay_public_service(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        is_public_service=True, activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    with pytest.raises(errors.CompanyCantBuyPublicServices):
        pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )


@injection_test
def test_balance_of_buyer_of_means_of_prod_reduced(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    price_total = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.means_account) == -price_total


@injection_test
def test_balance_of_buyer_of_raw_materials_reduced(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    price_total = pieces * plan.price_per_unit()
    assert (
        account_repository.get_account_balance(sender.raw_material_account)
        == -price_total
    )


@injection_test
def test_balance_of_seller_increased(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    price_total = pieces * plan.price_per_unit()
    assert (
        account_repository.get_account_balance(plan.planner.product_account)
        == price_total
    )


@injection_test
def test_correct_transaction_added_if_means_of_production_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    price_total = pieces * plan.price_per_unit()
    assert len(transaction_repository.transactions) == 1
    assert (
        transaction_repository.transactions[0].sending_account == sender.means_account
    )
    assert (
        transaction_repository.transactions[0].receiving_account
        == plan.planner.product_account
    )
    assert transaction_repository.transactions[0].amount == price_total


@injection_test
def test_correct_transaction_added_if_raw_materials_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    price_total = pieces * plan.price_per_unit()
    assert len(transaction_repository.transactions) == 1
    assert (
        transaction_repository.transactions[0].sending_account
        == sender.raw_material_account
    )
    assert (
        transaction_repository.transactions[0].receiving_account
        == plan.planner.product_account
    )
    assert transaction_repository.transactions[0].amount == price_total


@injection_test
def test_correct_purchase_added_if_means_of_production_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    purchase_repository: PurchaseRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    purchase_added = purchase_repository.purchases[0]
    assert len(purchase_repository.purchases) == 1
    assert purchase_added.plan == plan
    assert purchase_added.price_per_unit == plan.price_per_unit()
    assert purchase_added.amount == pieces
    assert purchase_added.purpose == PurposesOfPurchases.means_of_prod
    assert purchase_added.buyer == sender
    assert purchase_added.plan == plan


@injection_test
def test_correct_purchase_added_if_raw_materials_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    purchase_repository: PurchaseRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    purchase_added = purchase_repository.purchases[0]
    assert len(purchase_repository.purchases) == 1
    assert purchase_added.plan == plan
    assert purchase_added.price_per_unit == plan.price_per_unit()
    assert purchase_added.amount == pieces
    assert purchase_added.purpose == PurposesOfPurchases.raw_materials
    assert purchase_added.buyer == sender
    assert purchase_added.plan == plan


@injection_test
def test_plan_not_found_rejects_payment(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
) -> None:
    buyer = company_generator.create_company()
    response = pay_means_of_production(
        PayMeansOfProductionRequest(
            buyer=buyer.id,
            plan=uuid4(),
            amount=1,
            purpose=PurposesOfPurchases.means_of_prod,
        )
    )
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_not_found


@injection_test
def test_plan_found_accepts_payment(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
) -> None:
    buyer = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.min)
    response = pay_means_of_production(
        PayMeansOfProductionRequest(
            buyer=buyer.id,
            plan=plan.id,
            amount=1,
            purpose=PurposesOfPurchases.means_of_prod,
        )
    )
    assert not response.is_rejected
    assert response.rejection_reason is None
