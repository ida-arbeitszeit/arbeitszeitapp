from datetime import datetime, timedelta

from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    PlanGenerator,
    PurchaseGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.flask_integration.flask import FlaskTestCase


class CompanyPurchaseTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_by_default_no_company_purchases_are_in_db(self) -> None:
        assert not self.database_gateway.get_company_purchases()

    def test_that_there_are_some_company_purchases_in_db_after_one_was_created(
        self,
    ) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        assert self.database_gateway.get_company_purchases()

    def test_that_retrieved_purchase_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(plan=plan.id)
        purchase = self.database_gateway.get_company_purchases().first()
        assert purchase
        assert purchase.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        purchase_1 = self.database_gateway.get_company_purchases().first()
        purchase_2 = self.database_gateway.get_company_purchases().first()
        assert purchase_1
        assert purchase_2
        assert purchase_1.transaction_id == purchase_2.transaction_id

    def test_that_transaction_id_for_two_different_purchases_is_also_different(
        self,
    ) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        self.purchase_generator.create_resource_purchase_by_company()
        purchase_1, purchase_2 = list(self.database_gateway.get_company_purchases())
        assert purchase_1.transaction_id != purchase_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_purchase(
        self,
    ) -> None:
        expected_amount = 123
        self.purchase_generator.create_resource_purchase_by_company(
            amount=expected_amount
        )
        purchase = self.database_gateway.get_company_purchases().first()
        assert purchase
        assert purchase.amount == expected_amount

    def test_can_filter_purchases_by_company(self) -> None:
        company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        purchases = self.database_gateway.get_company_purchases()
        assert purchases.where_buyer_is_company(company)
        assert not purchases.where_buyer_is_company(other_company)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(plan=plan_1.id)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(plan=plan_2.id)
        purchase_1, purchase_2 = list(
            self.database_gateway.get_company_purchases().ordered_by_creation_date(
                ascending=True
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id
        purchase_2, purchase_1 = list(
            self.database_gateway.get_company_purchases().ordered_by_creation_date(
                ascending=False
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id

    def test_can_retrieve_plan_and_transaction_with_purchase(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        result = (
            self.database_gateway.get_company_purchases()
            .with_transaction_and_plan()
            .first()
        )
        assert result
        purchase, transaction, plan = result
        assert purchase.transaction_id == transaction.id
        assert purchase.plan_id == plan.id

    def test_can_retrieve_transaction_with_purchase(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        result = (
            self.database_gateway.get_company_purchases().with_transaction().first()
        )
        assert result
        purchase, transaction = result
        assert purchase.transaction_id == transaction.id

    def test_can_combine_filtering_and_joining_of_purchases_with_transactions_and_plans(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        assert (
            self.database_gateway.get_company_purchases()
            .ordered_by_creation_date()
            .where_buyer_is_company(company)
            .with_transaction_and_plan()
        )

    def test_can_combine_filtering_and_joining_of_purchases_with_transactions(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        assert (
            self.database_gateway.get_company_purchases()
            .ordered_by_creation_date()
            .where_buyer_is_company(company)
            .with_transaction()
        )

    def test_that_purchases_can_be_joined_with_transaction_and_provider(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        assert (
            self.database_gateway.get_company_purchases().with_transaction_and_provider()
        )

    def test_joining_with_transaction_and_provider_yields_same_transaction_as_when_just_joining_with_transaction(
        self,
    ) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        assert [
            transaction
            for _, transaction, _ in self.database_gateway.get_company_purchases().with_transaction_and_provider()
        ] == [
            transaction
            for _, transaction in self.database_gateway.get_company_purchases().with_transaction()
        ]

    def test_joining_with_transaction_and_provider_yields_same_purchase_as_when_not_joining(
        self,
    ) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        assert [
            purchase
            for purchase, _, _ in self.database_gateway.get_company_purchases().with_transaction_and_provider()
        ] == list(self.database_gateway.get_company_purchases())

    def test_joining_with_transaction_and_provider_yields_original_provider(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.purchase_generator.create_resource_purchase_by_company(plan=plan.id)
        assert [
            provider.id
            for _, _, provider in self.database_gateway.get_company_purchases().with_transaction_and_provider()
        ] == [provider]


class ConsumerPurchaseTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(1000)

    def test_that_by_default_no_member_purchases_are_in_db(self) -> None:
        assert not self.database_gateway.get_consumer_purchases()

    def test_that_there_are_some_member_purchases_in_db_after_one_was_created(
        self,
    ) -> None:
        self.purchase_generator.create_purchase_by_member()
        assert self.database_gateway.get_consumer_purchases()

    def test_that_retrieved_purchase_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan.id)
        purchase = self.database_gateway.get_consumer_purchases().first()
        assert purchase
        assert purchase.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.purchase_generator.create_purchase_by_member()
        purchase_1 = self.database_gateway.get_consumer_purchases().first()
        purchase_2 = self.database_gateway.get_consumer_purchases().first()
        assert purchase_1
        assert purchase_2
        assert purchase_1.transaction_id == purchase_2.transaction_id

    def test_that_transaction_id_for_two_different_purchases_is_also_different(
        self,
    ) -> None:
        self.purchase_generator.create_purchase_by_member()
        self.purchase_generator.create_purchase_by_member()
        purchase_1, purchase_2 = list(self.database_gateway.get_consumer_purchases())
        assert purchase_1.transaction_id != purchase_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_purchase(
        self,
    ) -> None:
        expected_amount = 123
        self.purchase_generator.create_purchase_by_member(amount=expected_amount)
        purchase = self.database_gateway.get_consumer_purchases().first()
        assert purchase
        assert purchase.amount == expected_amount

    def test_can_filter_purchases_by_member(self) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.purchase_generator.create_purchase_by_member(buyer=member)
        purchases = self.database_gateway.get_consumer_purchases()
        assert purchases.where_buyer_is_member(member)
        assert not purchases.where_buyer_is_member(other_member)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan_1.id)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan_2.id)
        purchase_1, purchase_2 = list(
            self.database_gateway.get_consumer_purchases().ordered_by_creation_date(
                ascending=True
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id
        purchase_2, purchase_1 = list(
            self.database_gateway.get_consumer_purchases().ordered_by_creation_date(
                ascending=False
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id

    def test_can_retrieve_plan_and_transaction_with_purchase(self) -> None:
        self.purchase_generator.create_purchase_by_member()
        result = (
            self.database_gateway.get_consumer_purchases()
            .with_transaction_and_plan()
            .first()
        )
        assert result
        purchase, transaction, plan = result
        assert purchase.transaction_id == transaction.id
        assert purchase.plan_id == plan.id

    def test_can_combine_filtering_and_joining_of_purchases_with_transactions_and_plans(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.purchase_generator.create_purchase_by_member(buyer=member)
        assert (
            self.database_gateway.get_consumer_purchases()
            .ordered_by_creation_date()
            .where_buyer_is_member(member)
            .with_transaction_and_plan()
        )
