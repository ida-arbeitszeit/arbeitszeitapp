import uuid
from decimal import Decimal

from arbeitszeit.use_cases import CreateOffer, CreateOfferRequest

from .dependency_injection import injection_test
from .repositories import OfferRepository


@injection_test
def test_that_create_offer_creates_an_offer(
    create_offer: CreateOffer, offer_repo: OfferRepository
):
    offer_request = CreateOfferRequest(
        name="testname",
        description="offer for test",
        plan_id=str(uuid.uuid4()),
        seller=uuid.uuid4(),
        price_per_unit=Decimal(5),
    )

    assert not len(offer_repo.offers)
    create_offer(offer_request)
    assert len(offer_repo.offers) == 1
