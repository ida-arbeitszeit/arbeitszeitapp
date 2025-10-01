from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from arbeitszeit.interactors import show_prd_account_details
from arbeitszeit.records import ProductionCosts
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.account_details import TransferPartyType
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class InteractorTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_prd_account_details.ShowPRDAccountDetailsInteractor
        )
        self.control_thresholds.set_allowed_overdraw_of_member_account(None)

    def test_no_transfers_returned_when_no_transfers_took_place(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
        )
        assert not response.transfers

    def test_balance_is_zero_when_no_transfers_took_place(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
        )
        assert response.account_balance == 0

    def test_company_id_is_returned(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
        )
        assert response.company_id == company

    def test_that_no_info_is_generated_after_company_consuming_p(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(consumer=consumer)
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=consumer)
        )
        assert len(response.transfers) == 0

    def test_that_no_info_is_generated_after_company_consuming_r(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=consumer)
        )
        assert len(response.transfers) == 0

    def test_that_no_transfers_are_shown_after_public_plan_is_accepted(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company, is_public_service=True)
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
        )
        assert len(response.transfers) == 0

    def test_that_three_transfers_are_shown_after_productive_plan_is_accepted(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
        )
        for transfer in response.transfers:
            assert transfer.volume < 0

    def test_that_four_transfers_are_shown_after_productive_plan_is_accepted_and_product_is_sold(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert len(response.transfers) == 4

    def test_that_transfers_are_shown_in_correct_descending_order(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert len(response.transfers) == 3
        self.consumption_generator.create_private_consumption(
            plan=plan,
            consumer=consumer,
            amount=1,
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert len(response.transfers) == 3
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert len(response.transfers) == 3
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan, consumer=consumer
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert len(response.transfers) == 4
        transfer_of_sale = response.transfers[0]
        assert transfer_of_sale.volume == Decimal(2)
        assert transfer_of_sale.type == TransferType.productive_consumption_r
        assert response.account_balance == Decimal(0)

    def test_that_plotting_info_is_empty_when_no_transfers_occurred(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=company)
        )
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_private_consumption(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_one_plan_approval_and_two_private_consumptions(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert len(response.plot.timestamps) == 5
        assert len(response.plot.accumulated_volumes) == 5
        assert transfer_1_timestamp in response.plot.timestamps
        assert transfer_2_timestamp in response.plot.timestamps
        assert response.plot.accumulated_volumes == [
            Decimal(0),  # credit for p
            Decimal(0),  # credit for r
            Decimal(-1),  # credit for a (-1)
            Decimal(0),  # consumption (+1)
            Decimal(2),  # consumption (+2)
        ]

    def test_that_party_type_for_credit_transfers_is_company_and_that_debtor_equals_creditor(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner
        )  # creates three credit transfers
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        for transfer in response.transfers:
            assert transfer.transfer_party.type == TransferPartyType.company
            assert transfer.debtor_equals_creditor

    def test_that_party_type_for_private_consumption_is_member(self) -> None:
        consumer = self.member_generator.create_member()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(
            plan=plan, consumer=consumer
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert response.transfers[0].transfer_party.type == TransferPartyType.member

    def test_that_party_type_for_fixed_means_consumption_is_company(self) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert response.transfers[0].transfer_party.type == TransferPartyType.company

    def test_that_party_type_for_resource_consumption_is_company(self) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan, consumer=consumer
        )
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        assert response.transfers[0].transfer_party.type == TransferPartyType.company

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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        transfer_party = response.transfers[0].transfer_party
        assert transfer_party.type == TransferPartyType.company
        assert transfer_party.id == consumer

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
        response = self.interactor.show_details(
            self.create_interactor_request(company_id=planner)
        )
        transfer_party = response.transfers[0].transfer_party
        assert transfer_party.type == TransferPartyType.company
        assert transfer_party.name == EXPECTED_CONSUMER_NAME

    def create_interactor_request(
        self, company_id: UUID
    ) -> show_prd_account_details.Request:
        return show_prd_account_details.Request(company_id=company_id)


class CompensationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_prd_account_details.ShowPRDAccountDetailsInteractor
        )

    def _get_cooperation_account(self) -> UUID:
        cooperation = self.cooperation_generator.create_cooperation()
        db = self.injector.get(DatabaseGateway)
        cooperation_record = db.get_cooperations().with_id(cooperation).first()
        assert cooperation_record
        return cooperation_record.account


class CompensationForCompanyTests(CompensationTests):
    def test_that_compensation_for_company_transfer_is_shown(self) -> None:
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            credit_account=planner.product_account,
            type=TransferType.compensation_for_company,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert any(
            t.type == TransferType.compensation_for_company for t in response.transfers
        )

    def test_that_same_value_as_in_transfer_is_shown(self) -> None:
        EXPECTED_VALUE = Decimal(12.123)
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            credit_account=planner.product_account,
            type=TransferType.compensation_for_company,
            value=EXPECTED_VALUE,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert len(response.transfers) == 1
        assert response.transfers[0].volume == EXPECTED_VALUE

    def test_that_same_date_as_in_transfer_is_shown(self) -> None:
        EXPECTED_DATE = datetime_utc(2022, 11, 1)
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            credit_account=planner.product_account,
            type=TransferType.compensation_for_company,
            date=EXPECTED_DATE,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert len(response.transfers) == 1
        assert response.transfers[0].date == EXPECTED_DATE

    def test_that_otrher_party_is_cooperation(self) -> None:
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            debit_account=self._get_cooperation_account(),
            credit_account=planner.product_account,
            type=TransferType.compensation_for_company,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert len(response.transfers) == 1
        assert response.transfers[0].transfer_party.type, TransferPartyType.cooperation


class CompensationForCoopTests(CompensationTests):
    def test_that_compensation_for_coop_transfer_is_shown(self) -> None:
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            debit_account=planner.product_account,
            type=TransferType.compensation_for_coop,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert any(
            t.type == TransferType.compensation_for_coop for t in response.transfers
        )

    def test_that_negative_value_from_transfer_is_shown(self) -> None:
        TRANSFER_VALUE = Decimal(12.123)
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            debit_account=planner.product_account,
            type=TransferType.compensation_for_coop,
            value=TRANSFER_VALUE,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert len(response.transfers) == 1
        assert response.transfers[0].volume == -TRANSFER_VALUE

    def test_that_same_date_as_in_transfer_is_shown(self) -> None:
        EXPECTED_DATE = datetime_utc(2022, 11, 1)
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            debit_account=planner.product_account,
            type=TransferType.compensation_for_coop,
            date=EXPECTED_DATE,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert len(response.transfers) == 1
        assert response.transfers[0].date == EXPECTED_DATE

    def test_that_other_party_is_cooperation(self) -> None:
        planner = self.company_generator.create_company_record()
        self.transfer_generator.create_transfer(
            debit_account=planner.product_account,
            credit_account=self._get_cooperation_account(),
            type=TransferType.compensation_for_coop,
        )
        response = self.interactor.show_details(
            show_prd_account_details.Request(company_id=planner.id)
        )
        assert len(response.transfers) == 1
        assert response.transfers[0].transfer_party.type, TransferPartyType.cooperation
