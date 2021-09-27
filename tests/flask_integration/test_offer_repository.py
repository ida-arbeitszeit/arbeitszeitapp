from datetime import datetime
from typing import List

from arbeitszeit.entities import ProductOffer
from project.database.repositories import ProductOfferRepository
from tests.data_generators import PlanGenerator

from .dependency_injection import injection_test


def offer_in_offers(offer: ProductOffer, offers: List[ProductOffer]):
    return offer.id in [o.id for o in offers]


@injection_test
def test_offers_can_be_created(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    assert not len(offer_repository)
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testname",
        description="testdescription",
    )
    assert len(offer_repository)


@injection_test
def test_get_all_offers_that_all_all_offers_are_returned(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    expected_offer1 = offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    expected_offer2 = offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer2",
        description="testdescription2",
    )
    all_offers = list(offer_repository.get_all_offers())
    assert offer_in_offers(expected_offer1, all_offers)
    assert offer_in_offers(expected_offer2, all_offers)


@injection_test
def test_that_all_offers_without_plan_duplicates_are_counted_correctly(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer2",
        description="testdescription2",
    )
    count_all_offers_no_duplicates = (
        offer_repository.count_all_offers_without_plan_duplicates()
    )
    assert count_all_offers_no_duplicates == 1
