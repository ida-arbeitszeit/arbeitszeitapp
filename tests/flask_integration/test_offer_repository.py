from datetime import datetime
from typing import List
from uuid import uuid4

import pytest

from arbeitszeit.entities import ProductOffer
from project.database.repositories import ProductOfferRepository
from project.error import PlanNotFound, ProductOfferNotFound
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
def test_that_offers_can_be_converted_from_and_to_orm_objects(
    offer_repo: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    original_offer = offer_repo.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testname",
        description="testdescription",
    )
    converted_offer = offer_repo.object_from_orm(
        offer_repo.object_to_orm(original_offer)
    )
    assert original_offer.id == converted_offer.id


@injection_test
def test_that_offers_cannot_be_be_retrieved_when_db_is_empty(
    offer_repo: ProductOfferRepository,
):
    with pytest.raises(ProductOfferNotFound):
        offer_repo.get_by_id(uuid4())


@injection_test
def test_that_offer_can_be_be_retrieved_by_its_id(
    offer_repo: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    original_offer = offer_repo.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testname",
        description="testdescription",
    )
    retrieved_offer = offer_repo.get_by_id(original_offer.id)
    assert original_offer.id == retrieved_offer.id


@injection_test
def test_that_get_all_offers_returns_empty_iterator_when_db_is_empty(
    offer_repository: ProductOfferRepository,
):
    all_offers = list(offer_repository.get_all_offers())
    assert len(all_offers) == 0


@injection_test
def test_that_get_all_offers_returns_all_offers(
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


@injection_test
def test_that_query_offers_by_name_does_return_empty_iterator_when_db_is_empty(
    offer_repository: ProductOfferRepository,
):
    result = offer_repository.query_offers_by_name("teststring")
    assert not list(result)


@injection_test
def test_that_query_offers_by_name_does_return_offer_where_name_is_exact_match(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer1 = offer_repository.create_offer(
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
    result = list(offer_repository.query_offers_by_name("testoffer1"))
    assert len(result) == 1
    assert result[0].id == offer1.id


@injection_test
def test_that_query_offers_by_name_does_return_offer_when_query_is_substring_of_name(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    offer2 = offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer2",
        description="testdescription2",
    )
    result = list(offer_repository.query_offers_by_name("ffer2"))
    assert len(result) == 1
    assert result[0].id == offer2.id


@injection_test
def test_that_query_offers_by_description_does_return_offer_where_description_is_exact_match(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer1 = offer_repository.create_offer(
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
    result = list(offer_repository.query_offers_by_description("testdescription1"))
    assert len(result) == 1
    assert result[0].id == offer1.id


@injection_test
def test_that_query_offers_by_description_does_return_offer_when_query_is_substring_of_description(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    offer2 = offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer2",
        description="testdescription2",
    )
    result = list(offer_repository.query_offers_by_description("ption2"))
    assert len(result) == 1
    assert result[0].id == offer2.id


@injection_test
def test_that_offer_can_be_deleted(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer = offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    assert len(offer_repository) == 1
    offer_repository.delete_offer(offer.id)
    assert len(offer_repository) == 0


@injection_test
def test_that_offer_does_not_get_deleted_when_wrong_id_is_provided(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    with pytest.raises(ProductOfferNotFound):
        offer_repository.delete_offer(uuid4())
    assert len(offer_repository) == 1


@injection_test
def test_that_get_all_offers_belonging_to_returns_only_offers_belonging_to_the_plan(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan1 = plan_generator.create_plan()
    offer1 = offer_repository.create_offer(
        plan=plan1,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    offer2 = offer_repository.create_offer(
        plan=plan1,
        creation_datetime=datetime.now(),
        name="testoffer2",
        description="testdescription2",
    )
    plan2 = plan_generator.create_plan()
    offer3 = offer_repository.create_offer(
        plan=plan2,
        creation_datetime=datetime.now(),
        name="testoffer3",
        description="testdescription3",
    )
    offers = offer_repository.get_all_offers_belonging_to(plan1.id)
    assert offer_in_offers(offer1, offers)
    assert offer_in_offers(offer2, offers)
    assert not offer_in_offers(offer3, offers)


@injection_test
def test_that_get_all_offers_belonging_to_returns_nothing_when_db_is_empty(
    offer_repository: ProductOfferRepository,
):
    with pytest.raises(PlanNotFound):
        results = offer_repository.get_all_offers_belonging_to(uuid4())
        assert results is None


@injection_test
def test_that_get_all_offers_belonging_to_returns_nothing_when_providing_wrong_plan_id(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testoffer1",
        description="testdescription1",
    )
    with pytest.raises(PlanNotFound):
        results = offer_repository.get_all_offers_belonging_to(uuid4())
        assert results is None
