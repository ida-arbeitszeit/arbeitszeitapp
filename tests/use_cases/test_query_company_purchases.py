from datetime import datetime, timedelta

from arbeitszeit.use_cases.query_company_purchases import QueryCompanyPurchases
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_purchases = self.injector.get(QueryCompanyPurchases)

    def test_that_no_purchase_is_returned_when_searching_an_empty_repo(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        results = list(self.query_purchases(company))
        assert not results

    def test_that_purchase_with_specified_plan_is_queried_after_purchase_for_this_plan_was_done(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_consumption_by_company(
            consumer=company, plan=plan.id
        )
        results = list(self.query_purchases(company))
        assert len(results) == 1
        latest_purchase = results[0]
        assert latest_purchase.plan_id == plan.id

    def test_latter_of_two_purchases_is_returned_first_other_one_is_returned_second(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        first_plan = self.plan_generator.create_plan().id
        second_plan = self.plan_generator.create_plan().id
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_consumption_by_company(
            consumer=company, plan=first_plan
        )
        self.datetime_service.advance_time(timedelta(days=1))
        self.purchase_generator.create_resource_consumption_by_company(
            consumer=company, plan=second_plan
        )
        results = list(self.query_purchases(company))
        assert results[0].plan_id == second_plan
        assert results[1].plan_id == first_plan
