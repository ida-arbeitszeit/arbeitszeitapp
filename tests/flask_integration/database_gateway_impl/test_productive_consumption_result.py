from datetime import datetime, timedelta
from uuid import uuid4

from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.data_generators import CompanyGenerator, ConsumptionGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.flask_integration.flask import FlaskTestCase


class ProductiveConsumptionResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_by_default_no_company_consumptions_are_in_db(self) -> None:
        assert not self.database_gateway.get_productive_consumptions()

    def test_that_there_are_some_company_consumptions_in_db_after_one_was_created(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert self.database_gateway.get_productive_consumptions()

    def test_that_retrieved_consumption_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(plan=plan.id)
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        assert consumption.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        consumption_1 = self.database_gateway.get_productive_consumptions().first()
        consumption_2 = self.database_gateway.get_productive_consumptions().first()
        assert consumption_1
        assert consumption_2
        assert consumption_1.transaction_id == consumption_2.transaction_id

    def test_that_transaction_id_for_two_different_consumptions_is_also_different(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        self.consumption_generator.create_resource_consumption_by_company()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_productive_consumptions()
        )
        assert consumption_1.transaction_id != consumption_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = 123
        self.consumption_generator.create_resource_consumption_by_company(
            amount=expected_amount
        )
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        assert consumption.amount == expected_amount

    def test_can_filter_consumptions_by_company(self) -> None:
        company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company
        )
        consumptions = self.database_gateway.get_productive_consumptions()
        assert consumptions.where_consumer_is_company(company)
        assert not consumptions.where_consumer_is_company(other_company)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan_1.id
        )
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan_2.id
        )
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
        self.consumption_generator.create_resource_consumption_by_company()
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
        self.consumption_generator.create_resource_consumption_by_company()
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
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company
        )
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
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company
        )
        assert (
            self.database_gateway.get_productive_consumptions()
            .ordered_by_creation_date()
            .where_consumer_is_company(company)
            .joined_with_transaction()
        )

    def test_that_consumptions_can_be_joined_with_transaction_and_provider(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert (
            self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        )

    def test_joining_with_transaction_and_provider_yields_same_transaction_as_when_just_joining_with_transaction(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
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
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            consumption
            for consumption, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        ] == list(self.database_gateway.get_productive_consumptions())

    def test_joining_with_transaction_and_provider_yields_original_provider(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan.id)
        assert [
            provider.id
            for _, _, provider in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_provider()
        ] == [provider]

    def test_no_consumption_is_returned_when_queried_providing_company_does_not_exist(
        self,
    ) -> None:
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            uuid4()
        )
        assert not result

    def test_no_consumption_is_returned_when_queried_company_is_not_provider(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company()
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            company
        )
        assert not result

    def test_consumption_is_returned_when_queried_company_is_provider(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan.id)
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            provider
        )
        assert result

    def test_two_consumptions_are_returned_when_queried_company_is_provider_for_two_productive_consumptions(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan.id)
        self.consumption_generator.create_fixed_means_consumption(plan=plan.id)
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            provider
        )
        assert len(result) == 2

    def test_one_consumption_is_returned_when_queried_company_is_provider_for_one_productive_and_one_private_consumption(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan.id)
        self.consumption_generator.create_private_consumption(plan=plan.id)
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            provider
        )
        assert len(result) == 1

    def test_that_consumptions_can_be_joined_with_transaction_and_plan_and_consumer(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert (
            self.database_gateway.get_productive_consumptions().joined_with_transaction_and_plan_and_consumer()
        )

    def test_joining_with_transaction_and_plan_and_consumer_yields_same_transaction_as_when_just_joining_with_transaction(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            transaction
            for _, transaction, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_plan_and_consumer()
        ] == [
            transaction
            for _, transaction in self.database_gateway.get_productive_consumptions().joined_with_transaction()
        ]

    def test_joining_with_transaction_and_plan_and_consumer_yields_same_consumption_as_when_not_joining(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            consumption
            for consumption, _, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_plan_and_consumer()
        ] == list(self.database_gateway.get_productive_consumptions())

    def test_joining_with_transaction_and_plan_and_consumer_yields_same_plan_as_when_just_joining_with_transaction_and_plan(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            plan
            for _, _, plan, _ in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_plan_and_consumer()
        ] == [
            plan
            for _, _, plan in self.database_gateway.get_productive_consumptions().joined_with_transactions_and_plan()
        ]

    def test_joining_with_transaction_and_plan_and_consumer_yields_original_consumer(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer
        )
        assert [
            consumer.id
            for _, _, _, consumer in self.database_gateway.get_productive_consumptions().joined_with_transaction_and_plan_and_consumer()
        ] == [consumer]
