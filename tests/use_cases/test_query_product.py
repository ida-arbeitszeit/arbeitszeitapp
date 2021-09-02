from typing import Iterable

from arbeitszeit.entities import ProductOffer
from arbeitszeit.use_cases import ProductFilter, ProductQueryResponse, QueryProducts
from tests.data_generators import OfferGenerator

from .dependency_injection import injection_test
from .repositories import OfferRepository


def offer_in_results(
    offer: ProductOffer, results: Iterable[ProductQueryResponse]
) -> bool:
    return offer.id in [result.offer_id for result in results]


@injection_test
def test_that_no_offer_is_returned_when_searching_an_empty_repository(
    query_products: QueryProducts,
):
    results = list(query_products(None, ProductFilter.by_name))
    assert not results
    results = list(query_products(None, ProductFilter.by_description))
    assert not results


@injection_test
def test_that_offers_where_name_is_exact_match_are_returned(
    query_products: QueryProducts,
    repository: OfferRepository,
    offer_generator: OfferGenerator,
):
    expected_offer = offer_generator.create_offer(name="My Product")
    results = list(query_products("My Product", ProductFilter.by_name))
    assert offer_in_results(expected_offer, results)


@injection_test
def test_query_substring_of_name_returns_correct_result(
    query_products: QueryProducts,
    repository: OfferRepository,
    offer_generator: OfferGenerator,
):
    expected_offer = offer_generator.create_offer(name="My Product")
    results = list(query_products("Product", ProductFilter.by_name))
    assert offer_in_results(expected_offer, results)


@injection_test
def test_that_offers_where_description_is_exact_match_are_returned(
    query_products: QueryProducts,
    repository: OfferRepository,
    offer_generator: OfferGenerator,
):
    description = "my description"
    expected_offer = offer_generator.create_offer(description=description)
    results = list(query_products(description, ProductFilter.by_description))
    assert offer_in_results(expected_offer, results)


@injection_test
def test_query_substrin_of_description_returns_correct_result(
    query_products: QueryProducts,
    repository: OfferRepository,
    offer_generator: OfferGenerator,
):
    expected_offer = offer_generator.create_offer(description="my description")
    results = list(query_products("description", ProductFilter.by_description))
    assert offer_in_results(expected_offer, results)
