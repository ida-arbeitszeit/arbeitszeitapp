from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.records import ProductionCosts
from tests.flask_integration.flask import FlaskTestCase


class ProductiveConsumptionResultTests(FlaskTestCase):
    def test_that_by_default_no_company_consumptions_are_in_db(self) -> None:
        assert not self.database_gateway.get_productive_consumptions()

    def test_that_there_are_some_company_consumptions_in_db_after_one_was_created(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert self.database_gateway.get_productive_consumptions()

    def test_that_retrieved_consumption_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        consumption = self.database_gateway.get_productive_consumptions().first()
        assert consumption
        assert consumption.plan_id == plan

    def test_that_transfer_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        consumption_1 = self.database_gateway.get_productive_consumptions().first()
        consumption_2 = self.database_gateway.get_productive_consumptions().first()
        assert consumption_1
        assert consumption_2
        assert (
            consumption_1.transfer_of_productive_consumption
            == consumption_2.transfer_of_productive_consumption
        )

    def test_that_transfer_id_for_two_different_consumptions_is_also_different(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        self.consumption_generator.create_resource_consumption_by_company()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_productive_consumptions()
        )
        assert (
            consumption_1.transfer_of_productive_consumption
            != consumption_2.transfer_of_productive_consumption
        )

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

    def test_that_transfer_of_compensation_exists_after_consumption_of_underproductive_plan(
        self,
    ) -> None:
        plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(50), Decimal(100)]
        )
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plans[1]
        )  # second plan is underproductive
        consumptions = list(self.database_gateway.get_productive_consumptions())
        assert len(consumptions) == 1
        assert consumptions[0].transfer_of_compensation

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
        self.consumption_generator.create_resource_consumption_by_company(plan=plan_1)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(plan=plan_2)
        consumption_1, consumption_2 = list(
            self.database_gateway.get_productive_consumptions().ordered_by_creation_date(
                ascending=True
            )
        )
        assert consumption_1.plan_id == plan_1
        assert consumption_2.plan_id == plan_2
        consumption_2, consumption_1 = list(
            self.database_gateway.get_productive_consumptions().ordered_by_creation_date(
                ascending=False
            )
        )
        assert consumption_1.plan_id == plan_1
        assert consumption_2.plan_id == plan_2

    def test_can_retrieve_plan_and_transfer_with_consumption(self) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        result = (
            self.database_gateway.get_productive_consumptions()
            .joined_with_transfer_and_plan()
            .first()
        )
        assert result
        consumption, transfer, plan = result
        assert consumption.transfer_of_productive_consumption == transfer.id
        assert consumption.plan_id == plan.id

    def test_can_retrieve_transfer_with_consumption(self) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        result = (
            self.database_gateway.get_productive_consumptions()
            .joined_with_transfer()
            .first()
        )
        assert result
        consumption, transfer = result
        assert consumption.transfer_of_productive_consumption == transfer.id

    def test_can_combine_filtering_and_joining_of_consumptions_with_transfer_and_plan(
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
            .joined_with_transfer_and_plan()
        )

    def test_can_combine_filtering_and_joining_of_consumptions_with_transfer(
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
            .joined_with_transfer()
        )

    def test_that_consumptions_can_be_joined_with_transfer_and_provider(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert (
            self.database_gateway.get_productive_consumptions().joined_with_transfer_and_provider()
        )

    def test_joining_with_transfer_and_provider_yields_same_transfer_as_when_just_joining_with_transfer(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            transfer
            for _, transfer, _ in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_provider()
        ] == [
            transfer
            for _, transfer in self.database_gateway.get_productive_consumptions().joined_with_transfer()
        ]

    def test_joining_with_transfer_and_provider_yields_same_consumption_as_when_not_joining(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            consumption
            for consumption, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_provider()
        ] == list(self.database_gateway.get_productive_consumptions())

    def test_joining_with_transfer_and_provider_yields_original_provider(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        assert [
            provider.id
            for _, _, provider in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_provider()
        ] == [provider]

    def test_that_consumptions_joined_with_transfer_and_plan_and_consumer_yields_at_least_one_result_if_there_exists_one_resource_consumption(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert (
            self.database_gateway.get_productive_consumptions().joined_with_transfer_and_plan_and_consumer()
        )

    def test_joining_with_transfer_and_plan_and_consumer_yields_same_transfer_as_when_just_joining_with_transfer(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            transfer
            for _, transfer, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_plan_and_consumer()
        ] == [
            transfer
            for _, transfer in self.database_gateway.get_productive_consumptions().joined_with_transfer()
        ]

    def test_joining_with_transfer_and_plan_and_consumer_yields_same_consumption_as_when_not_joining(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            consumption
            for consumption, _, _, _ in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_plan_and_consumer()
        ] == list(self.database_gateway.get_productive_consumptions())

    def test_joining_with_transfer_and_plan_and_consumer_yields_same_plan_as_when_just_joining_with_transfer_and_plan(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        assert [
            plan
            for _, _, plan, _ in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_plan_and_consumer()
        ] == [
            plan
            for _, _, plan in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_plan()
        ]

    def test_joining_with_transfer_and_plan_and_consumer_yields_original_consumer(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer
        )
        assert [
            consumer.id
            for _, _, _, consumer in self.database_gateway.get_productive_consumptions().joined_with_transfer_and_plan_and_consumer()
        ] == [consumer]

    def create_cooperating_plans_with(
        self, *, costs_per_unit: list[Decimal]
    ) -> list[UUID]:
        plans = [self.create_plan_with(cost_per_unit=cost) for cost in costs_per_unit]
        self.cooperation_generator.create_cooperation(
            plans=plans,
        )
        return plans

    def create_plan_with(self, *, cost_per_unit: Decimal) -> UUID:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=cost_per_unit,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        return plan


class FilterWhereProviderIsCompanyTests(FlaskTestCase):
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
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            provider
        )
        assert result

    def test_two_consumptions_are_returned_when_queried_company_is_provider_for_two_productive_consumptions(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            provider
        )
        assert len(result) == 2

    def test_one_consumption_is_returned_when_queried_company_is_provider_for_one_productive_and_one_private_consumption(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        self.consumption_generator.create_private_consumption(plan=plan)
        result = self.database_gateway.get_productive_consumptions().where_provider_is_company(
            provider
        )
        assert len(result) == 1
