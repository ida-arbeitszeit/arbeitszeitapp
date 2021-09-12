from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from project.database.repositories import ProductOfferRepository

from .dependency_injection import injection_test


@injection_test
def tests_offers_can_be_created(
    offer_repository: ProductOfferRepository,
):
    assert not len(offer_repository)
    offer_repository.create_offer(
        plan_id=uuid4(),
        creation_datetime=datetime.now(),
        name="testname",
        description="testdescription",
        seller=uuid4(),
        price_per_unit=Decimal(3),
    )
    assert len(offer_repository)
