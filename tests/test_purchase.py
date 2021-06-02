import pytest

from arbeitszeit.use_cases import PurchaseProduct
from tests.data_generators import MemberGenerator, OfferGenerator
from tests.dependency_injection import injection_test


@injection_test
def test_purchase_amount_can_not_exceed_supply(
    purchase_product: PurchaseProduct,
    offer_generator: OfferGenerator,
    member_generator: MemberGenerator,
):
    offer = offer_generator.create_offer(amount=1)
    buyer = member_generator.create_member()
    with pytest.raises(AssertionError):
        purchase_product(offer, 2, "consumption", buyer)
