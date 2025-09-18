from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.interactors import show_r_account_details
from arbeitszeit.records import ProductionCosts
from arbeitszeit.transfers.transfer_type import TransferType
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class InteractorTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_r_account_details.ShowRAccountDetailsInteractor
        )

    def test_no_transfers_returned_when_company_has_neither_consumed_nor_planned_r(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert not response.transfers

    def test_balance_is_zero_when_company_has_neither_consumed_nor_planned_r(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert response.account_balance == 0

    def test_balance_is_zero_when_company_has_consumed_the_same_amount_of_r_as_it_has_planned(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company, costs=ProductionCosts(Decimal(0), Decimal(3), Decimal(0))
        )
        plan_to_be_consumed = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)), amount=1
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company, amount=1, plan=plan_to_be_consumed
        )
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert response.account_balance == 0

    def test_id_of_the_company_that_owns_the_account_is_returned(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert response.company_id == company

    def test_that_no_transfers_are_generated_after_company_passed_on_a_consumer_product(
        self,
    ) -> None:
        producer = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=producer)
        transfers_before_consumption = len(
            self.interactor.show_details(
                self.create_interactor_request(producer)
            ).transfers
        )
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.interactor.show_details(
            self.create_interactor_request(producer)
        )
        assert len(response.transfers) == transfers_before_consumption

    def test_that_no_transfers_are_generated_after_company_passed_on_a_means_of_production(
        self,
    ) -> None:
        producer = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=producer)
        transfers_before_consumption = len(
            self.interactor.show_details(
                self.create_interactor_request(producer)
            ).transfers
        )

        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.interactor.show_details(
            self.create_interactor_request(producer)
        )
        assert len(response.transfers) == transfers_before_consumption

    def test_that_one_transfer_is_shown_when_plan_gets_approved(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        response = self.interactor.show_details(self.create_interactor_request(planner))
        assert len(response.transfers) == 1

    def test_that_two_transfers_are_shown_when_plan_gets_approved_and_company_consumes_r(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=planner
        )
        response = self.interactor.show_details(self.create_interactor_request(planner))
        assert len(response.transfers) == 2

    def test_that_newest_transfers_are_shown_first(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2025, 1, 1))
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        self.datetime_service.advance_time(timedelta(days=1))
        self.plan_generator.create_plan(planner=planner, is_public_service=True)
        self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=planner
        )
        response = self.interactor.show_details(self.create_interactor_request(planner))
        assert response.transfers[0].type == TransferType.productive_consumption_r
        assert response.transfers[1].type == TransferType.credit_public_r
        assert response.transfers[2].type == TransferType.credit_r

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_correct_info_for_credit_is_shown(
        self, is_public_service: bool
    ) -> None:
        EXPECTED_VOLUME = Decimal(8.5)
        EXPECTED_TIMESTAMP = datetime_utc(2025, 1, 1)
        EXPECTED_TRANSFER_TYPE = (
            TransferType.credit_public_r if is_public_service else TransferType.credit_r
        )
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(EXPECTED_TIMESTAMP)
        self.plan_generator.create_plan(
            planner=company,
            is_public_service=is_public_service,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=EXPECTED_VOLUME,
                means_cost=Decimal(1),
            ),
        )
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert len(response.transfers) == 1
        assert response.transfers[0].volume == EXPECTED_VOLUME
        assert isinstance(response.transfers[0].date, datetime)
        assert response.transfers[0].type == EXPECTED_TRANSFER_TYPE
        assert response.account_balance == EXPECTED_VOLUME

    def test_that_after_consumption_of_liquid_means_one_transfer_of_that_type_is_shown(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer
        )

        response = self.interactor.show_details(
            self.create_interactor_request(consumer)
        )
        transfer = response.transfers[0]
        assert transfer.type == TransferType.productive_consumption_r

    def test_that_after_consumption_of_liquid_means_one_transfer_with_volume_of_negated_costs_is_shown(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        expected_volume = -costs.total_cost()
        plan = self.plan_generator.create_plan(costs=costs, amount=1)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer, plan=plan, amount=1
        )

        response = self.interactor.show_details(
            self.create_interactor_request(consumer)
        )
        transfer = response.transfers[0]
        assert transfer.volume == expected_volume

    def test_that_after_consumption_of_liquid_means_the_balance_equals_the_negated_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        expected_balance = -costs.total_cost()
        plan = self.plan_generator.create_plan(costs=costs, amount=1)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer, plan=plan, amount=1
        )

        response = self.interactor.show_details(
            self.create_interactor_request(consumer)
        )
        assert response.account_balance == expected_balance

    def test_that_after_consumption_of_two_liquid_means_the_r_balance_equals_negated_sum_of_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs1 = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        costs2 = ProductionCosts(Decimal(4), Decimal(5), Decimal(6))
        expected_balance = -(costs1.total_cost() + costs2.total_cost())
        plan1 = self.plan_generator.create_plan(costs=costs1, amount=1)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer, plan=plan1, amount=1
        )
        plan2 = self.plan_generator.create_plan(costs=costs2, amount=1)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer, plan=plan2, amount=1
        )

        response = self.interactor.show_details(
            self.create_interactor_request(consumer)
        )
        assert response.account_balance == expected_balance

    def test_that_plotting_info_is_empty_when_no_transfers_occurred(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_consumption_of_liquid_means(
        self,
    ) -> None:
        own_company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        other_companys_plan = self.plan_generator.create_plan(
            planner=other_company,
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=own_company,
            plan=other_companys_plan,
        )
        response = self.interactor.show_details(
            self.create_interactor_request(own_company)
        )
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_consumption_of_two_liquid_means(
        self,
    ) -> None:
        AMOUNT_PRODUCED = 50
        TOTAL_COSTS = Decimal(10)
        COSTS_PER_CONSUMPTION = TOTAL_COSTS / AMOUNT_PRODUCED
        CONSUMPTION_1 = 10
        CONSUMPTION_2 = 20
        PLAN_APPROVED_DATE = datetime_utc(2025, 1, 1)
        CONSUMPTION_DATE_1 = datetime_utc(2025, 1, 2)
        CONSUMPTION_DATE_2 = datetime_utc(2025, 1, 3)

        own_company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.datetime_service.freeze_time(PLAN_APPROVED_DATE)
        other_companys_plan = self.plan_generator.create_plan(
            planner=other_company,
            costs=ProductionCosts(
                labour_cost=TOTAL_COSTS / 3,
                resource_cost=TOTAL_COSTS / 3,
                means_cost=TOTAL_COSTS / 3,
            ),
            amount=AMOUNT_PRODUCED,
        )
        self.datetime_service.freeze_time(CONSUMPTION_DATE_1)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_1,
        )
        self.datetime_service.freeze_time(CONSUMPTION_DATE_2)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_2,
        )
        response = self.interactor.show_details(
            self.create_interactor_request(own_company)
        )
        assert len(response.plot.timestamps) == 2

        assert len(response.plot.accumulated_volumes) == 2

        assert CONSUMPTION_DATE_1 in response.plot.timestamps
        assert CONSUMPTION_DATE_2 in response.plot.timestamps

        assert (
            CONSUMPTION_1 * COSTS_PER_CONSUMPTION * (-1)
            in response.plot.accumulated_volumes
        )
        assert (
            CONSUMPTION_1 * COSTS_PER_CONSUMPTION * (-1)
            + CONSUMPTION_2 * COSTS_PER_CONSUMPTION * (-1)
        ) in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_three_consumptions_of_raw_materials(
        self,
    ) -> None:
        own_company = self.company_generator.create_company()

        TIME_OF_FIRST_CONSUMPTION = datetime_utc(2025, 1, 1)
        TIME_OF_SECOND_CONSUMPTION = datetime_utc(2025, 1, 3)
        TIME_OF_THIRD_CONSUMPTION = datetime_utc(2025, 1, 5)

        VALUE_OF_FIRST_CONSUMPTION = Decimal(10)
        VALUE_OF_SECOND_CONSUMPTION = Decimal(12.5)
        VALUE_OF_THIRD_CONSUMPTION = Decimal(27.2)

        self.datetime_service.freeze_time(TIME_OF_FIRST_CONSUMPTION)
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=VALUE_OF_FIRST_CONSUMPTION,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=own_company,
            plan=plan_1,
            amount=1,
        )
        self.datetime_service.freeze_time(TIME_OF_SECOND_CONSUMPTION)
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=VALUE_OF_SECOND_CONSUMPTION,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=own_company,
            plan=plan_2,
            amount=1,
        )
        self.datetime_service.freeze_time(TIME_OF_THIRD_CONSUMPTION)
        plan_3 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=VALUE_OF_THIRD_CONSUMPTION,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=own_company,
            plan=plan_3,
            amount=1,
        )

        response = self.interactor.show_details(
            self.create_interactor_request(own_company)
        )
        assert response.plot.timestamps[0] == TIME_OF_FIRST_CONSUMPTION
        assert response.plot.timestamps[1] == TIME_OF_SECOND_CONSUMPTION
        assert response.plot.timestamps[2] == TIME_OF_THIRD_CONSUMPTION

        assert response.plot.accumulated_volumes[0] == VALUE_OF_FIRST_CONSUMPTION * (-1)
        assert response.plot.accumulated_volumes[1] == (
            VALUE_OF_FIRST_CONSUMPTION * (-1) + VALUE_OF_SECOND_CONSUMPTION * (-1)
        )
        assert response.plot.accumulated_volumes[2] == (
            VALUE_OF_FIRST_CONSUMPTION * (-1)
            + VALUE_OF_SECOND_CONSUMPTION * (-1)
            + VALUE_OF_THIRD_CONSUMPTION * (-1)
        )

    def test_that_correct_plotting_info_is_generated_after_receiving_of_credit_for_liquid_means_of_production(
        self,
    ) -> None:
        PLAN_APPROVED_DATE = datetime_utc(2025, 1, 1)
        EXPECTED_VOLUME = Decimal(8.5)
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(PLAN_APPROVED_DATE)
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=EXPECTED_VOLUME,
                means_cost=Decimal(0),
            ),
        )
        self.datetime_service.unfreeze_time()
        response = self.interactor.show_details(self.create_interactor_request(company))
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes
        assert len(response.plot.timestamps) == 1
        assert len(response.plot.accumulated_volumes) == 1
        assert PLAN_APPROVED_DATE in response.plot.timestamps
        assert EXPECTED_VOLUME in response.plot.accumulated_volumes

    def create_interactor_request(
        self, company_id: UUID
    ) -> show_r_account_details.Request:
        return show_r_account_details.Request(company=company_id)
