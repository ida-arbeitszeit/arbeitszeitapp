from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import ProductionCosts
from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases import show_prd_account_details

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            show_prd_account_details.ShowPRDAccountDetailsUseCase
        )
        self.control_thresholds.set_allowed_overdraw_of_member_account(10000)

    def test_no_transfers_returned_when_no_transfers_took_place(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert not response.transfers

    def test_balance_is_zero_when_no_transfers_took_place(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert response.account_balance == 0

    def test_company_id_is_returned(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert response.company_id == company

    def test_that_no_info_is_generated_after_company_consuming_p(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(consumer=consumer)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=consumer)
        )
        assert len(response.transfers) == 0

    def test_that_no_info_is_generated_after_company_consuming_r(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=consumer)
        )
        assert len(response.transfers) == 0

    def test_that_no_transfers_are_shown_after_public_plan_is_accepted(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company, is_public_service=True)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert len(response.transfers) == 0

    def test_that_three_transfers_are_shown_after_productive_plan_is_accepted(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert len(response.transfers) == 3

    def test_that_credit_transfers_have_correct_values(self) -> None:
        EXPECTED_CREDIT_P = Decimal(2)
        EXPECTED_CREDIT_R = Decimal(3)
        EXPECTED_CREDIT_A = Decimal(4.5)
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                means_cost=EXPECTED_CREDIT_P,
                resource_cost=EXPECTED_CREDIT_R,
                labour_cost=EXPECTED_CREDIT_A,
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert len(response.transfers) == 3
        for transfer in response.transfers:
            match transfer.type:
                case TransferType.credit_p:
                    assert transfer.volume == -EXPECTED_CREDIT_P
                case TransferType.credit_r:
                    assert transfer.volume == -EXPECTED_CREDIT_R
                case TransferType.credit_a:
                    assert transfer.volume == -EXPECTED_CREDIT_A
                case _:
                    raise ValueError(f"Unexpected transfer type: {transfer.type}")

    def test_that_credit_transfers_are_negative(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
                labour_cost=Decimal(1),
            ),
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        for transfer in response.transfers:
            assert transfer.volume < 0

    def test_that_four_transfers_are_shown_after_productive_plan_is_accepted_and_product_is_sold(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 4

    def test_that_transfers_are_shown_in_correct_descending_order(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        transfers = response.transfers
        assert transfers[0].type == TransferType.productive_consumption_r
        assert transfers[1].type == TransferType.productive_consumption_p
        assert transfers[2].type == TransferType.private_consumption
        assert transfers[3].type in [
            TransferType.credit_p,
            TransferType.credit_r,
            TransferType.credit_a,
        ]
        assert transfers[4].type in [
            TransferType.credit_p,
            TransferType.credit_r,
            TransferType.credit_a,
        ]
        assert transfers[5].type in [
            TransferType.credit_p,
            TransferType.credit_r,
            TransferType.credit_a,
        ]

    def test_that_correct_info_is_generated_after_private_consumption(
        self,
    ) -> None:
        consumer = self.member_generator.create_member()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 3
        self.consumption_generator.create_private_consumption(
            plan=plan,
            consumer=consumer,
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 4
        transfer_of_sale = response.transfers[0]
        assert transfer_of_sale.volume == Decimal(2)
        assert transfer_of_sale.type == TransferType.private_consumption
        assert response.account_balance == Decimal(0)

    def test_that_correct_info_is_generated_after_fixed_means_consumption(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 3
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 4
        transfer_of_sale = response.transfers[0]
        assert transfer_of_sale.volume == Decimal(2)
        assert transfer_of_sale.type == TransferType.productive_consumption_p
        assert response.account_balance == Decimal(0)

    def test_that_correct_info_is_generated_after_resource_consumption(self) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 3
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transfers) == 4
        transfer_of_sale = response.transfers[0]
        assert transfer_of_sale.volume == Decimal(2)
        assert transfer_of_sale.type == TransferType.productive_consumption_r
        assert response.account_balance == Decimal(0)

    def test_that_plotting_info_is_empty_when_no_transfers_occurred(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_private_consumption(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_one_plan_approval_and_two_private_consumptions(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(1), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        transfer_1_timestamp = self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=1)
        transfer_2_timestamp = self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=2)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.plot.timestamps) == 5
        assert len(response.plot.accumulated_volumes) == 5
        assert transfer_1_timestamp in response.plot.timestamps
        assert transfer_2_timestamp in response.plot.timestamps
        assert response.plot.accumulated_volumes == [
            Decimal(-1),  # a
            Decimal(-1),  # r
            Decimal(-1),  # p
            Decimal(0),  # consumption
            Decimal(2),  # consumption
        ]

    def test_that_peer_type_for_credit_transfers_is_none(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        for transfer in response.transfers:
            assert transfer.peer is None

    def test_that_peer_type_for_private_consumption_is_member(self) -> None:
        consumer = self.member_generator.create_member()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert response.transfers[0].peer is not None
        assert isinstance(
            response.transfers[0].peer, show_prd_account_details.MemberPeer
        )

    def test_that_peer_type_for_fixed_means_consumption_is_company(self) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert response.transfers[0].peer is not None
        assert isinstance(
            response.transfers[0].peer, show_prd_account_details.CompanyPeer
        )

    def test_that_peer_type_for_resource_consumption_is_company(self) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert response.transfers[0].peer is not None
        assert isinstance(
            response.transfers[0].peer, show_prd_account_details.CompanyPeer
        )

    def test_that_correct_consumer_id_is_shown_after_productive_consumption(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        company_peer = response.transfers[0].peer
        assert isinstance(company_peer, show_prd_account_details.CompanyPeer)
        assert company_peer.id == consumer

    def test_that_correct_consumer_name_is_shown_when_company_sold_to_company(
        self,
    ) -> None:
        EXPECTED_CONSUMER_NAME = "Consumer Company"
        consumer = self.company_generator.create_company(name=EXPECTED_CONSUMER_NAME)
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        company_peer = response.transfers[0].peer
        assert isinstance(company_peer, show_prd_account_details.CompanyPeer)
        assert company_peer.name == EXPECTED_CONSUMER_NAME

    def create_use_case_request(
        self, company_id: UUID
    ) -> show_prd_account_details.Request:
        return show_prd_account_details.Request(company_id=company_id)
