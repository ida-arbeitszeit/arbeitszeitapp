from typing import Iterable

from arbeitszeit.entities import Purchase
from arbeitszeit.use_cases import PurchaseQueryResponse, QueryPurchases
from tests.data_generators import CompanyGenerator, MemberGenerator, PurchaseGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


def purchase_in_results(
    purchase: Purchase, results: Iterable[PurchaseQueryResponse]
) -> bool:
    return purchase.plan in [result.plan_id for result in results]


@injection_test
def test_that_no_purchase_is_returned_when_searching_an_empty_repo(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member = member_generator.create_member()
    results = list(query_purchases(member))
    assert not results
    company = company_generator.create_company()
    results = list(query_purchases(company))
    assert not results


@injection_test
def test_that_correct_purchases_are_returned(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
    company_generator: CompanyGenerator,
):
    member = member_generator.create_member()
    company = company_generator.create_company()
    expected_purchase_member = purchase_generator.create_purchase_by_member(
        buyer=member
    )
    expected_purchase_company = purchase_generator.create_purchase_by_company(
        buyer=company
    )
    results = list(query_purchases(member))
    assert len(results) == 1
    assert purchase_in_results(expected_purchase_member, results)
    assert not purchase_in_results(expected_purchase_company, results)
    results = list(query_purchases(company))
    assert len(results) == 1
    assert purchase_in_results(expected_purchase_company, results)
    assert not purchase_in_results(expected_purchase_member, results)


@injection_test
def test_that_purchases_are_returned_in_correct_order_when_member_queries(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
    datetime_service: FakeDatetimeService,
):
    member = member_generator.create_member()
    # Creating older purchase first to test correct ordering
    purchase_generator.create_purchase_by_member(
        buyer=member, purchase_date=datetime_service.now_minus_two_days()
    )
    expected_recent_purchase = purchase_generator.create_purchase_by_member(
        buyer=member, purchase_date=datetime_service.now_minus_one_day()
    )
    results = list(query_purchases(member))
    assert purchase_in_results(
        expected_recent_purchase, [results[0]]
    )  # more recent purchase is first


@injection_test
def test_that_purchases_are_returned_in_correct_order_when_company_queries(
    query_purchases: QueryPurchases,
    purchase_generator: PurchaseGenerator,
    company_generator: CompanyGenerator,
    datetime_service: FakeDatetimeService,
):
    company = company_generator.create_company()
    # Creating older purchase first to test correct ordering
    purchase_generator.create_purchase_by_company(
        buyer=company, purchase_date=datetime_service.now_minus_two_days()
    )
    expected_recent_purchase = purchase_generator.create_purchase_by_company(
        buyer=company, purchase_date=datetime_service.now_minus_one_day()
    )
    results = list(query_purchases(company))
    assert purchase_in_results(
        expected_recent_purchase, [results[0]]
    )  # more recent purchase is first
