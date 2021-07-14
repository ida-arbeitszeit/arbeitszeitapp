import pytest

from arbeitszeit.entities import AccountTypes, PurposesOfPurchases
from arbeitszeit.use_cases import PurchaseProduct
from tests.data_generators import CompanyGenerator, MemberGenerator, OfferGenerator
from tests.dependency_injection import injection_test
from tests.repositories import PurchaseRepository, TransactionRepository


@injection_test
def test_purchase_amount_can_not_exceed_supply(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    transaction_repository: TransactionRepository,
    purchase_repository: PurchaseRepository,
):
    offer = offer_generator.create_offer(amount=1)
    buyer = member_generator.create_member()
    with pytest.raises(AssertionError):
        purchase_product(
            purchase_repository,
            transaction_repository,
            offer,
            2,
            PurposesOfPurchases.consumption,
            buyer,
        )


@injection_test
def test_product_offer_decreased_after_purchase(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    transaction_repository: TransactionRepository,
    purchase_repository: PurchaseRepository,
):
    offer = offer_generator.create_offer(amount=5)
    buyer = member_generator.create_member()
    purchase_product(
        purchase_repository,
        transaction_repository,
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
    transaction_repository: TransactionRepository,
    purchase_repository: PurchaseRepository,
):
    offer = offer_generator.create_offer(amount=3)
    buyer = member_generator.create_member()
    purchase_product(
        purchase_repository,
        transaction_repository,
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
    transaction_repository: TransactionRepository,
    purchase_repository: PurchaseRepository,
    company_generator: CompanyGenerator,
):
    # member, consumption
    offer1 = offer_generator.create_offer(amount=3)
    buyer1 = member_generator.create_member()
    purpose1 = PurposesOfPurchases.consumption
    purchase_product(
        purchase_repository, transaction_repository, offer1, 3, purpose1, buyer1
    )
    assert buyer1.account.balance == -3

    # company, means of production
    offer2 = offer_generator.create_offer(amount=3)
    buyer2 = company_generator.create_company()
    purpose2 = PurposesOfPurchases.means_of_prod
    purchase_product(
        purchase_repository, transaction_repository, offer2, 3, purpose2, buyer2
    )
    assert buyer2.means_account.balance == -3

    # company, raw materials
    offer3 = offer_generator.create_offer(amount=3)
    buyer3 = company_generator.create_company()
    purpose3 = PurposesOfPurchases.raw_materials
    purchase_product(
        purchase_repository, transaction_repository, offer3, 3, purpose3, buyer3
    )
    assert buyer3.raw_material_account.balance == -3


@injection_test
def test_balance_of_seller_increased(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    transaction_repository: TransactionRepository,
    purchase_repository: PurchaseRepository,
):
    offer = offer_generator.create_offer(amount=3)
    buyer = member_generator.create_member()
    purchase_product(
        purchase_repository,
        transaction_repository,
        offer,
        3,
        PurposesOfPurchases.consumption,
        buyer,
    )
    assert offer.provider.product_account.balance == 3


@injection_test
def test_correct_transaction_added_to_repo(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
    transaction_repository: TransactionRepository,
    purchase_repository: PurchaseRepository,
    company_generator: CompanyGenerator,
):
    # member, consumption
    offer1 = offer_generator.create_offer(amount=3)
    buyer1 = member_generator.create_member()
    purpose1 = PurposesOfPurchases.consumption
    purchase_product(
        purchase_repository, transaction_repository, offer1, 3, purpose1, buyer1
    )
    added_transaction_account_type = (
        transaction_repository.transactions.pop().account_from.account_type
    )
    member_account_type = AccountTypes.member.value
    assert added_transaction_account_type == member_account_type

    # company, means of production
    offer2 = offer_generator.create_offer(amount=3)
    buyer2 = company_generator.create_company()
    purpose2 = PurposesOfPurchases.means_of_prod
    purchase_product(
        purchase_repository, transaction_repository, offer2, 3, purpose2, buyer2
    )
    added_transaction_account_type = (
        transaction_repository.transactions.pop().account_from.account_type
    )
    means_account_type = AccountTypes.p.value
    assert added_transaction_account_type == means_account_type

    # company, raw materials
    offer3 = offer_generator.create_offer(amount=3)
    buyer3 = company_generator.create_company()
    purpose3 = PurposesOfPurchases.raw_materials
    purchase_product(
        purchase_repository, transaction_repository, offer3, 3, purpose3, buyer3
    )

    added_transaction_account_type = (
        transaction_repository.transactions.pop().account_from.account_type
    )
    raw_material_account_type = AccountTypes.r.value
    assert added_transaction_account_type == raw_material_account_type
