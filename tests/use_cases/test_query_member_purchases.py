from typing import Iterable

from arbeitszeit.entities import Purchase
from arbeitszeit.use_cases import PurchaseQueryResponse, QueryMemberPurchases
from tests.data_generators import MemberGenerator, PurchaseGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


def purchase_in_results(
    purchase: Purchase, results: Iterable[PurchaseQueryResponse]
) -> bool:
    return purchase.plan in [result.plan_id for result in results]


@injection_test
def test_that_no_purchase_is_returned_when_searching_an_empty_repo(
    query_purchases: QueryMemberPurchases,
    member_generator: MemberGenerator,
):
    member = member_generator.create_member_entity()
    results = list(query_purchases(member))
    assert not results


@injection_test
def test_that_correct_purchases_are_returned(
    query_purchases: QueryMemberPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
):
    member = member_generator.create_member_entity()
    expected_purchase_member = purchase_generator.create_purchase_by_member(
        buyer=member
    )
    results = list(query_purchases(member))
    assert len(results) == 1
    assert purchase_in_results(expected_purchase_member, results)


@injection_test
def test_that_purchases_are_returned_in_correct_order(
    query_purchases: QueryMemberPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
    datetime_service: FakeDatetimeService,
):
    member = member_generator.create_member_entity()
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
