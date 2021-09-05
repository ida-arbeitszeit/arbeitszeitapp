from decimal import Decimal

import pytest

from arbeitszeit.entities import AccountTypes, ProductionCosts, PurposesOfPurchases
from arbeitszeit.errors import CompanyCantBuyPublicServices
from arbeitszeit.use_cases import PurchaseProduct
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    OfferGenerator,
    PlanGenerator,
)

from .dependency_injection import injection_test
from .repositories import AccountRepository, TransactionRepository


@injection_test
def test_purchase_amount_can_not_exceed_supply(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
):
    offer = offer_generator.create_offer(amount=1)
    buyer = member_generator.create_member()
    with pytest.raises(AssertionError):
        purchase_product(
            offer,
            2,
            PurposesOfPurchases.consumption,
            buyer,
        )


@injection_test
def test_company_cant_buy_public_service(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(is_public_service=True)
    offer = offer_generator.create_offer(amount=1, plan=plan)
    buyer = company_generator.create_company()
    with pytest.raises(CompanyCantBuyPublicServices):
        purchase_product(
            offer,
            2,
            PurposesOfPurchases.raw_materials,
            buyer,
        )


@injection_test
def test_product_offer_decreased_after_purchase(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
):
    offer = offer_generator.create_offer(amount=5)
    buyer = member_generator.create_member()
    purchase_product(
        offer,
        2,
        PurposesOfPurchases.consumption,
        buyer,
    )
    assert offer.amount_available == 3


@injection_test
def test_product_offer_deactivated_if_amount_zero(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
):
    offer = offer_generator.create_offer(amount=3)
    buyer = member_generator.create_member()
    purchase_product(
        offer,
        3,
        PurposesOfPurchases.consumption,
        buyer,
    )
    assert not offer.active


@injection_test
def test_balance_of_buyer_reduced(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    # member, consumption
    plan = plan_generator.create_plan(
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)), amount=3
    )
    offer1 = offer_generator.create_offer(amount=3, plan=plan)
    buyer1 = member_generator.create_member()
    purpose1 = PurposesOfPurchases.consumption
    purchase_product(offer1, 3, purpose1, buyer1)
    expected_reduction = -3 * offer1.price_per_unit()
    assert account_repository.get_account_balance(buyer1.account) == expected_reduction

    # company, means of production
    offer2 = offer_generator.create_offer(amount=3)
    buyer2 = company_generator.create_company()
    purpose2 = PurposesOfPurchases.means_of_prod
    purchase_product(offer2, 3, purpose2, buyer2)
    expected_reduction = -3 * offer2.price_per_unit()
    assert (
        account_repository.get_account_balance(buyer2.means_account)
        == expected_reduction
    )

    # company, raw materials
    offer3 = offer_generator.create_offer(amount=3)
    buyer3 = company_generator.create_company()
    purpose3 = PurposesOfPurchases.raw_materials
    purchase_product(offer3, 3, purpose3, buyer3)
    expected_reduction = -3 * offer3.price_per_unit()
    assert (
        account_repository.get_account_balance(buyer3.raw_material_account)
        == expected_reduction
    )


@injection_test
def test_balance_of_buyer_not_reduced_when_buying_public_service(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    plan1 = plan_generator.create_plan(is_public_service=True)
    offer1 = offer_generator.create_offer(amount=3, plan=plan1)
    buyer1 = member_generator.create_member()
    purpose1 = PurposesOfPurchases.consumption
    purchase_product(offer1, 3, purpose1, buyer1)
    expected_reduction = 0
    assert account_repository.get_account_balance(buyer1.account) == expected_reduction


@injection_test
def test_balance_of_seller_increased(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    plan = plan_generator.create_plan(
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)), amount=3
    )
    offer = offer_generator.create_offer(amount=3, plan=plan)
    buyer = member_generator.create_member()
    purchase_product(
        offer,
        3,
        PurposesOfPurchases.consumption,
        buyer,
    )
    expected_increase = offer.price_per_unit() * 3
    assert (
        account_repository.get_account_balance(offer.plan.planner.product_account)
        == expected_increase
    )


@injection_test
def test_balance_of_planner_not_increased_when_offering_public_service(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    plan = plan_generator.create_plan(is_public_service=True)
    offer = offer_generator.create_offer(amount=3, plan=plan)
    buyer = member_generator.create_member()
    purchase_product(
        offer,
        3,
        PurposesOfPurchases.consumption,
        buyer,
    )
    expected_increase = 0
    assert (
        account_repository.get_account_balance(offer.plan.planner.product_account)
        == expected_increase
    )


@injection_test
def test_correct_transaction_added_to_repo_when_buying_public_service(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    transaction_repository: TransactionRepository,
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan(is_public_service=True)
    offer1 = offer_generator.create_offer(amount=3, plan=plan1)
    buyer1 = member_generator.create_member()
    purpose1 = PurposesOfPurchases.consumption
    purchase_product(offer1, 3, purpose1, buyer1)
    added_transaction_account_type = (
        transaction_repository.transactions.pop().sending_account.account_type
    )
    assert added_transaction_account_type == AccountTypes.member
