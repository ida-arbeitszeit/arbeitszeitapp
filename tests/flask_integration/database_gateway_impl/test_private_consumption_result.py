from datetime import datetime, timedelta

from tests.control_thresholds import ControlThresholdsTestImpl
from tests.flask_integration.flask import FlaskTestCase


class PrivateConsumptionTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(1000)

    def test_that_by_default_no_private_consumptions_are_in_db(self) -> None:
        assert not self.database_gateway.get_private_consumptions()

    def test_that_there_are_some_private_consumptions_in_db_after_one_was_created(
        self,
    ) -> None:
        self.consumption_generator.create_private_consumption()
        assert self.database_gateway.get_private_consumptions()

    def test_that_retrieved_consumption_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(plan=plan)
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        assert consumption.plan_id == plan

    def test_that_transfer_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.consumption_generator.create_private_consumption()
        consumption_1 = self.database_gateway.get_private_consumptions().first()
        consumption_2 = self.database_gateway.get_private_consumptions().first()
        assert consumption_1
        assert consumption_2
        assert (
            consumption_1.transfer_of_private_consumption
            == consumption_2.transfer_of_private_consumption
        )

    def test_that_transfer_id_for_two_different_consumptions_is_also_different(
        self,
    ) -> None:
        self.consumption_generator.create_private_consumption()
        self.consumption_generator.create_private_consumption()
        consumption_1, consumption_2 = list(
            self.database_gateway.get_private_consumptions()
        )
        assert (
            consumption_1.transfer_of_private_consumption
            != consumption_2.transfer_of_private_consumption
        )

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_consumption(
        self,
    ) -> None:
        expected_amount = 123
        self.consumption_generator.create_private_consumption(amount=expected_amount)
        consumption = self.database_gateway.get_private_consumptions().first()
        assert consumption
        assert consumption.amount == expected_amount

    def test_can_filter_consumptions_by_member(self) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=member)
        consumptions = self.database_gateway.get_private_consumptions()
        assert consumptions.where_consumer_is_member(member)
        assert not consumptions.where_consumer_is_member(other_member)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(plan=plan_1)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(plan=plan_2)
        consumption_1, consumption_2 = list(
            self.database_gateway.get_private_consumptions().ordered_by_creation_date(
                ascending=True
            )
        )
        assert consumption_1.plan_id == plan_1
        assert consumption_2.plan_id == plan_2
        consumption_2, consumption_1 = list(
            self.database_gateway.get_private_consumptions().ordered_by_creation_date(
                ascending=False
            )
        )
        assert consumption_1.plan_id == plan_1
        assert consumption_2.plan_id == plan_2

    def test_can_retrieve_plan_and_transfer_with_consumption(self) -> None:
        self.consumption_generator.create_private_consumption()
        result = (
            self.database_gateway.get_private_consumptions()
            .joined_with_transfer_and_plan()
            .first()
        )
        assert result
        consumption, transfer, plan = result
        assert consumption.transfer_of_private_consumption == transfer.id
        assert consumption.plan_id == plan.id

    def test_can_combine_filtering_and_joining_of_consumptions_with_transfer_and_plan(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=member)
        assert (
            self.database_gateway.get_private_consumptions()
            .ordered_by_creation_date()
            .where_consumer_is_member(member)
            .joined_with_transfer_and_plan()
        )

    def test_exclude_consumptions_of_products_from_other_providers_when_filtering_by_providing_company(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_private_consumption(plan=plan)
        consumptions = self.database_gateway.get_private_consumptions()
        assert not consumptions.where_provider_is_company(other_company)

    def test_that_consumptions_of_products_from_provider_are_included_when_filtering_by_providing_company(
        self,
    ) -> None:
        provider = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_private_consumption(plan=plan)
        consumptions = self.database_gateway.get_private_consumptions()
        assert consumptions.where_provider_is_company(provider)

    def test_can_retrieve_plan_and_transaction_and_consumer_with_consumption(
        self,
    ) -> None:
        expected_consumer = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(
            consumer=expected_consumer
        )
        result = (
            self.database_gateway.get_private_consumptions()
            .joined_with_transfer_and_plan_and_consumer()
            .first()
        )
        assert result
        consumption, transfer, plan, consumer = result
        assert consumption.transfer_of_private_consumption == transfer.id
        assert consumption.plan_id == plan.id
        assert consumer.id == expected_consumer
