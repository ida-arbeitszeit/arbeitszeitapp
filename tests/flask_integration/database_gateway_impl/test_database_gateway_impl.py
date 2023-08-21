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


class CompanyConsumptionTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_by_default_no_company_consumptions_are_in_db(self) -> None:
        assert not self.database_gateway.get_productive_consumptions()

    def test_that_there_are_some_company_consumptions_in_db_after_one_was_created(
        self,
    ) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        assert self.database_gateway.get_productive_consumptions()

    def test_that_retrieved_consumption_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_consumption_by_company(plan=plan.id)
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        assert consumption.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        consumption_1 = self.database_gateway.get_productive_consumptions().first()
        consumption_2 = self.database_gateway.get_productive_consumptions().first()
        assert consumption_1
        assert consumption_2
        assert consumption_1.transaction_id == consumption_2.transaction_id

    def test_that_transaction_id_for_two_different_consumptions_is_also_different(
        self,
    ) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        self.purchase_generator.create_resource_consumption_by_company()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_productive_consumptions()
        )
        assert consumption_1.transaction_id != consumption_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = 123
        self.purchase_generator.create_resource_consumption_by_company(
            amount=expected_amount
        )
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        assert consumption.amount == expected_amount

    def test_can_filter_consumptions_by_company(self) -> None:
        company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.purchase_generator.create_resource_consumption_by_company(consumer=company)
        consumptions = self.database_gateway.get_productive_consumptions()
        assert consumptions.where_consumer_is_company(company)
        assert not consumptions.where_consumer_is_company(other_company)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_consumption_by_company(plan=plan_1.id)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_consumption_by_company(plan=plan_2.id)
        consumption_1, consumption_2 = list(
            self.database_gateway.get_productive_consumptions().ordered_by_creation_date(
                ascending=True
            )
        )
        assert consumption_1.plan_id == plan_1.id
        assert consumption_2.plan_id == plan_2.id
        consumption_2, consumption_1 = list(
            self.database_gateway.get_productive_consumptions().ordered_by_creation_date(
                ascending=False
            )
        )
        assert consumption_1.plan_id == plan_1.id
        assert consumption_2.plan_id == plan_2.id

    def test_can_retrieve_plan_and_transaction_with_consumption(self) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        result = (
            self.database_gateway.get_productive_consumptions()
            .joined_with_transactions_and_plan()
            .first()
        )
        assert result
        consumption, transaction, plan = result
        assert consumption.transaction_id == transaction.id
        assert consumption.plan_id == plan.id

    def test_can_retrieve_transaction_with_consumption(self) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        result = (
            self.database_gateway.get_productive_consumptions()
            .joined_with_transaction()
            .first()
        )
        assert result
        consumption, transaction = result
        assert consumption.transaction_id == transaction.id

    def test_can_combine_filtering_and_joining_of_consumptions_with_transactions_and_plans(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_consumption_by_company(consumer=company)
        assert (
            self.database_gateway.get_productive_consumptions()
            .ordered_by_creation_date()
            .where_consumer_is_company(company)
            .joined_with_transactions_and_plan()
        )

    def test_can_combine_filtering_and_joining_of_consumptions_with_transactions(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_consumption_by_company(consumer=company)
        assert (
            self.database_gateway.get_productive_consumptions()
            .ordered_by_creation_date()
            .where_consumer_is_company(company)
            .joined_with_transaction()
        )

    def test_that_consumptions_can_be_joined_with_transaction_and_provider(
        self,
    ) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        assert (
            self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        )

    def test_joining_with_transaction_and_provider_yields_same_transaction_as_when_just_joining_with_transaction(
        self,
    ) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        assert [
            transaction
            for _, transaction, _ in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        ] == [
            transaction
            for _, transaction in self.database_gateway.get_productive_consumptions().joined_with_transaction()
        ]

    def test_joining_with_transaction_and_provider_yields_same_consumption_as_when_not_joining(
        self,
    ) -> None:
        self.purchase_generator.create_resource_consumption_by_company()
        assert [
            consumption
            for consumption, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        ] == list(self.database_gateway.get_productive_consumptions())

    def test_joining_with_transaction_and_provider_yields_original_provider(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.purchase_generator.create_resource_consumption_by_company(plan=plan.id)
        assert [
            provider.id
            for _, _, provider in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        ] == [provider]


class PrivateConsumptionTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(1000)

    def test_that_by_default_no_private_consumptions_are_in_db(self) -> None:
        assert not self.database_gateway.get_private_consumptions()

    def test_that_there_are_some_private_consumptions_in_db_after_one_was_created(
        self,
    ) -> None:
        self.purchase_generator.create_private_consumption()
        assert self.database_gateway.get_private_consumptions()

    def test_that_retrieved_consumption_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_private_consumption(plan=plan.id)
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        assert consumption.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.purchase_generator.create_private_consumption()
        consumption_1 = self.database_gateway.get_private_consumptions().first()
        consumption_2 = self.database_gateway.get_private_consumptions().first()
        assert consumption_1
        assert consumption_2
        assert consumption_1.transaction_id == consumption_2.transaction_id

    def test_that_transaction_id_for_two_different_consumptions_is_also_different(
        self,
    ) -> None:
        self.purchase_generator.create_private_consumption()
        self.purchase_generator.create_private_consumption()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_private_consumptions()
        )
        assert consumption_1.transaction_id != consumption_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = 123
        self.purchase_generator.create_private_consumption(amount=expected_amount)
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        assert consumption.amount == expected_amount

    def test_can_filter_consumptions_by_member(self) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.purchase_generator.create_private_consumption(consumer=member)
        consumptions = self.database_gateway.get_private_consumptions()
        assert consumptions.where_consumer_is_member(member)
        assert not consumptions.where_consumer_is_member(other_member)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.purchase_generator.create_private_consumption(plan=plan_1.id)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.purchase_generator.create_private_consumption(plan=plan_2.id)
        consumption_1, consumption_2 = list(
            self.database_gateway.get_private_consumptions().ordered_by_creation_date(
                ascending=True
            )
        )
        assert consumption_1.plan_id == plan_1.id
        assert consumption_2.plan_id == plan_2.id
        consumption_2, consumption_1 = list(
            self.database_gateway.get_private_consumptions().ordered_by_creation_date(
                ascending=False
            )
        )
        assert consumption_1.plan_id == plan_1.id
        assert consumption_2.plan_id == plan_2.id

    def test_can_retrieve_plan_and_transaction_with_consumption(self) -> None:
        self.purchase_generator.create_private_consumption()
        result = (
            self.database_gateway.get_private_consumptions()
            .joined_with_transactions_and_plan()
            .first()
        )
        assert result
        consumption, transaction, plan = result
        assert consumption.transaction_id == transaction.id
        assert consumption.plan_id == plan.id

    def test_can_combine_filtering_and_joining_of_consumptions_with_transactions_and_plans(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.purchase_generator.create_private_consumption(consumer=member)
        assert (
            self.database_gateway.get_private_consumptions()
            .ordered_by_creation_date()
            .where_consumer_is_member(member)
            .joined_with_transactions_and_plan()
        )
