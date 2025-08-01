from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases.show_p_account_details import ShowPAccountDetailsUseCase

from .base_test_case import BaseTestCase


class ShowPAccountDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ShowPAccountDetailsUseCase)

    def test_no_transfers_returned_when_company_has_not_consumed_or_planned(
        self,
    ) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert not response.transfers

    def test_balance_is_zero_when_company_has_not_consumed_or_planned(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.account_balance == 0

    def test_balance_is_zero_when_company_has_only_planned_r_and_a(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(1),
                means_cost=Decimal(0),
            ),
        )
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.account_balance == 0

    def test_balance_is_zero_when_company_has_consumed_the_same_amount_of_p_as_it_has_planned(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company, costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(3))
        )
        plan_to_be_consumed = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)), amount=1
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=company, amount=1, plan=plan_to_be_consumed
        )
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.account_balance == 0

    def test_id_of_the_company_that_owns_the_account_is_returned(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.company_id == company

    def test_that_no_transfers_are_generated_after_company_passed_on_a_consumer_product(
        self,
    ) -> None:
        producer = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=producer)
        transfers_before_consumption = len(
            self.use_case.show_details(self.create_use_case_request(producer)).transfers
        )
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(self.create_use_case_request(producer))
        assert len(response.transfers) == transfers_before_consumption

    def test_that_no_transfers_are_generated_after_company_passed_on_a_means_of_production(
        self,
    ) -> None:
        producer = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=producer)
        transfers_before_consumption = len(
            self.use_case.show_details(self.create_use_case_request(producer)).transfers
        )

        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.show_details(self.create_use_case_request(producer))
        assert len(response.transfers) == transfers_before_consumption

    def test_that_one_transfer_is_shown_when_company_has_a_plan_approved(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert len(response.transfers) == 1

    def test_that_one_transfer_is_shown_when_company_consumes_p(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(consumer=consumer)
        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert len(response.transfers) == 1

    def test_that_two_transfers_are_shown_when_company_has_plan_approved_and_consumes_p(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_fixed_means_consumption(consumer=planner)
        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert len(response.transfers) == 2

    def test_that_newest_transfers_are_shown_first(self) -> None:
        self.datetime_service.freeze_time(datetime(2025, 1, 1))
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        self.datetime_service.advance_time(timedelta(days=1))
        self.plan_generator.create_plan(planner=planner, is_public_service=True)
        self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_fixed_means_consumption(consumer=planner)
        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert len(response.transfers) == 3
        assert response.transfers[0].type == TransferType.productive_consumption_p
        assert response.transfers[1].type == TransferType.credit_public_p
        assert response.transfers[2].type == TransferType.credit_p

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_correct_transfer_info_for_credit_is_shown(
        self,
        is_public_service: bool,
    ) -> None:
        EXPECTED_VOLUME = Decimal(8.5)
        EXPECTED_TIMESTAMP = datetime(2025, 1, 1)
        EXPECTED_TRANSFER_TYPE = (
            TransferType.credit_public_p if is_public_service else TransferType.credit_p
        )
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(EXPECTED_TIMESTAMP)
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(1),
                means_cost=EXPECTED_VOLUME,
            ),
            is_public_service=is_public_service,
        )
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert len(response.transfers) == 1
        assert response.transfers[0].volume == EXPECTED_VOLUME
        assert response.transfers[0].date == EXPECTED_TIMESTAMP
        assert response.transfers[0].type == EXPECTED_TRANSFER_TYPE
        assert response.account_balance == EXPECTED_VOLUME

    def test_that_after_consumption_of_fixed_means_of_production_one_transfer_of_that_type_is_shown(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(consumer=consumer)

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert len(response.transfers) == 1
        transfer = response.transfers[0]
        assert transfer.type == TransferType.productive_consumption_p

    def test_that_after_consumption_of_fixed_means_one_transfer_with_volume_of_negated_costs_is_shown(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        expected_volume = -costs.total_cost()
        plan = self.plan_generator.create_plan(costs=costs, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert len(response.transfers) == 1
        transfer = response.transfers[0]
        assert transfer.volume == expected_volume

    def test_that_after_consumption_of_fixed_means_the_balance_equals_the_negated_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        expected_balance = -costs.total_cost()
        plan = self.plan_generator.create_plan(costs=costs, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert response.account_balance == expected_balance

    def test_that_after_consumption_of_two_fixed_means_the_p_balance_equals_negated_sum_of_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs1 = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        costs2 = ProductionCosts(Decimal(4), Decimal(5), Decimal(6))
        expected_balance = -(costs1.total_cost() + costs2.total_cost())
        plan1 = self.plan_generator.create_plan(costs=costs1, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan1, amount=1
        )
        plan2 = self.plan_generator.create_plan(costs=costs2, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan2, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert response.account_balance == expected_balance

    def test_that_plotting_info_is_empty_when_no_transfers_occurred(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.use_case.show_details(self.create_use_case_request(company))
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_consumption_of_fixed_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        other_companys_plan = self.plan_generator.create_plan(
            planner=other_company,
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=own_company,
            plan=other_companys_plan,
        )
        response = self.use_case.show_details(self.create_use_case_request(own_company))
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_consumption_of_two_fixed_means_of_production(
        self,
    ) -> None:
        AMOUNT_PRODUCED = 50
        TOTAL_COSTS = Decimal(10)
        COSTS_PER_CONSUMPTION = TOTAL_COSTS / AMOUNT_PRODUCED
        CONSUMPTION_1 = 10
        CONSUMPTION_2 = 20
        PLAN_APPROVED_DATE = datetime(2025, 1, 1)
        CONSUMPTION_DATE_1 = datetime(2025, 1, 2)
        CONSUMPTION_DATE_2 = datetime(2025, 1, 3)

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
        self.consumption_generator.create_fixed_means_consumption(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_1,
        )
        self.datetime_service.freeze_time(CONSUMPTION_DATE_2)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_2,
        )
        self.datetime_service.unfreeze_time()
        response = self.use_case.show_details(self.create_use_case_request(own_company))
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

    def test_that_plotting_info_is_generated_in_the_correct_order_after_consumption_of_three_fixed_means_of_production(
        self,
    ) -> None:
        AMOUNT_PRODUCED = 50
        TOTAL_COSTS = Decimal(10)
        COSTS_PER_CONSUMPTION = TOTAL_COSTS / AMOUNT_PRODUCED
        CONSUMPTION_1 = 10
        CONSUMPTION_2 = 20
        CONSUMPTION_3 = 30
        PLAN_APPROVED_DATE = datetime(2025, 1, 1)
        CONSUMPTION_DATE_1 = datetime(2025, 1, 2)
        CONSUMPTION_DATE_2 = datetime(2025, 1, 3)
        CONSUMPTION_DATE_3 = datetime(2025, 1, 4)

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
        self.consumption_generator.create_fixed_means_consumption(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_1,
        )
        self.datetime_service.freeze_time(CONSUMPTION_DATE_2)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_2,
        )
        self.datetime_service.freeze_time(CONSUMPTION_DATE_3)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=own_company,
            plan=other_companys_plan,
            amount=CONSUMPTION_3,
        )
        self.datetime_service.unfreeze_time()
        response = self.use_case.show_details(self.create_use_case_request(own_company))
        assert response.plot.timestamps[0] == CONSUMPTION_DATE_1
        assert response.plot.timestamps[1] == CONSUMPTION_DATE_2
        assert response.plot.timestamps[2] == CONSUMPTION_DATE_3

        assert response.plot.accumulated_volumes[
            0
        ] == CONSUMPTION_1 * COSTS_PER_CONSUMPTION * (-1)
        assert response.plot.accumulated_volumes[1] == (
            CONSUMPTION_1 * COSTS_PER_CONSUMPTION * (-1)
            + CONSUMPTION_2 * COSTS_PER_CONSUMPTION * (-1)
        )
        assert response.plot.accumulated_volumes[2] == (
            CONSUMPTION_1 * COSTS_PER_CONSUMPTION * (-1)
            + CONSUMPTION_2 * COSTS_PER_CONSUMPTION * (-1)
            + CONSUMPTION_3 * COSTS_PER_CONSUMPTION * (-1)
        )

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_correct_plotting_info_is_generated_after_receiving_of_credit_for_fixed_means_of_production(
        self,
        is_public_service: bool,
    ) -> None:
        PLAN_APPROVED_DATE = datetime(2025, 1, 1)
        EXPECTED_VOLUME = Decimal(8.5)
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(PLAN_APPROVED_DATE)
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal(0),
                means_cost=EXPECTED_VOLUME,
            ),
            is_public_service=is_public_service,
        )
        self.datetime_service.unfreeze_time()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

        assert len(response.plot.timestamps) == 1
        assert len(response.plot.accumulated_volumes) == 1

        assert PLAN_APPROVED_DATE in response.plot.timestamps
        assert EXPECTED_VOLUME in response.plot.accumulated_volumes

    def create_use_case_request(
        self, company_id: UUID
    ) -> ShowPAccountDetailsUseCase.Request:
        return ShowPAccountDetailsUseCase.Request(company=company_id)
