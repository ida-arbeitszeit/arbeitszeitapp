from typing import Iterable

from arbeitszeit.entities import Purchase
from arbeitszeit.use_cases import PurchaseQueryResponse, QueryMemberPurchases
from tests.use_cases.base_test_case import BaseTestCase


class TestQueryMemberPurchases(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_purchases = self.injector.get(QueryMemberPurchases)

    def assertPurchaseInResults(
        self, purchase: Purchase, results: Iterable[PurchaseQueryResponse]
    ) -> bool:
        return purchase.plan in [result.plan_id for result in results]

    def test_that_no_purchase_is_returned_when_searching_an_empty_repo(self):
        member = self.member_generator.create_member()
        results = list(self.query_purchases(member))
        assert not results

    def test_that_correct_purchases_are_returned(self):
        member = self.member_generator.create_member_entity()
        expected_purchase_member = self.purchase_generator.create_purchase_by_member(
            buyer=member
        )
        results = list(self.query_purchases(member.id))
        assert len(results) == 1
        assert self.assertPurchaseInResults(expected_purchase_member, results)

    def test_that_purchases_are_returned_in_correct_order(self):
        member = self.member_generator.create_member_entity()
        # Creating older purchase first to test correct ordering
        self.purchase_generator.create_purchase_by_member(
            buyer=member, purchase_date=self.datetime_service.now_minus_two_days()
        )
        expected_recent_purchase = self.purchase_generator.create_purchase_by_member(
            buyer=member, purchase_date=self.datetime_service.now_minus_one_day()
        )
        results = list(self.query_purchases(member.id))
        assert self.assertPurchaseInResults(
            expected_recent_purchase, [results[0]]
        )  # more recent purchase is first
