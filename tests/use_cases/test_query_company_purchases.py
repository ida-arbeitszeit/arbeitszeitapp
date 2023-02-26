from typing import Iterable

from arbeitszeit.entities import Purchase
from arbeitszeit.use_cases.query_company_purchases import (
    PurchaseQueryResponse,
    QueryCompanyPurchases,
)
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_purchases = self.injector.get(QueryCompanyPurchases)

    def purchase_in_results(
        self, purchase: Purchase, results: Iterable[PurchaseQueryResponse]
    ) -> bool:
        return purchase.plan in [result.plan_id for result in results]

    def test_that_no_purchase_is_returned_when_searching_an_empty_repo(
        self,
    ):
        company = self.company_generator.create_company()
        results = list(self.query_purchases(company))
        assert not results

    def test_that_correct_purchases_are_returned(self):
        company = self.company_generator.create_company_entity()
        expected_purchase_company = self.purchase_generator.create_purchase_by_company(
            buyer=company
        )
        results = list(self.query_purchases(company.id))
        assert len(results) == 1
        assert self.purchase_in_results(expected_purchase_company, results)

    def test_that_purchases_are_returned_in_correct_order(self):
        company = self.company_generator.create_company_entity()
        # Creating older purchase first to test correct ordering
        self.purchase_generator.create_purchase_by_company(
            buyer=company, purchase_date=self.datetime_service.now_minus_two_days()
        )
        expected_recent_purchase = self.purchase_generator.create_purchase_by_company(
            buyer=company, purchase_date=self.datetime_service.now_minus_one_day()
        )
        results = list(self.query_purchases(company.id))
        assert self.purchase_in_results(
            expected_recent_purchase, [results[0]]
        )  # more recent purchase is first
