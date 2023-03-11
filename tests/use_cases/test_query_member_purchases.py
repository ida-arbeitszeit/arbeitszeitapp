from datetime import datetime, timedelta

from arbeitszeit.use_cases.query_member_purchases import QueryMemberPurchases
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.use_cases.base_test_case import BaseTestCase


class TestQueryMemberPurchases(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_purchases = self.injector.get(QueryMemberPurchases)
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(10000)

    def test_that_no_purchase_is_returned_when_searching_an_empty_repo(self) -> None:
        member = self.member_generator.create_member()
        results = list(self.query_purchases(member))
        assert not results

    def test_that_correct_purchases_are_returned(self) -> None:
        expected_plan = self.plan_generator.create_plan().id
        member = self.member_generator.create_member()
        self.purchase_generator.create_purchase_by_member(
            buyer=member, plan=expected_plan
        )
        results = list(self.query_purchases(member))
        assert len(results) == 1
        assert results[0].plan_id == expected_plan

    def test_that_purchases_are_returned_in_correct_order(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        first_plan = self.plan_generator.create_plan().id
        second_plan = self.plan_generator.create_plan().id
        member = self.member_generator.create_member()
        self.purchase_generator.create_purchase_by_member(buyer=member, plan=first_plan)
        self.datetime_service.advance_time(timedelta(days=1))
        self.purchase_generator.create_purchase_by_member(
            buyer=member, plan=second_plan
        )
        results = list(self.query_purchases(member))
        assert results[0].plan_id == second_plan
        assert results[1].plan_id == first_plan
