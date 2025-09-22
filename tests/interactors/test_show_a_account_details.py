from datetime import timedelta
from uuid import UUID

from arbeitszeit.interactors import show_a_account_details
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_min_utc
from tests.interactors.base_test_case import BaseTestCase


class InteractorTestBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_a_account_details.ShowAAccountDetailsInteractor
        )
        self.company = self.company_generator.create_company_record()
        self.work_account = self.company.work_account

    def create_interactor_request(
        self, company_id: UUID
    ) -> show_a_account_details.Request:
        return show_a_account_details.Request(company=company_id)


class ShowWorkAccountTests(InteractorTestBase):
    def test_company_id_from_request_is_returned(self):
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.company_id == self.company.id


class WorkAccountBalanceTests(InteractorTestBase):
    def test_balance_is_zero_when_no_transfers_took_place(self) -> None:
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.account_balance == 0

    def test_balance_is_zero_when_transfer_took_place_to_other_account_of_company(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(
            debit_account=self.company.means_account
        )
        self.transfer_generator.create_transfer(
            debit_account=self.company.raw_material_account
        )
        self.transfer_generator.create_transfer(
            debit_account=self.company.product_account
        )
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.account_balance == 0

    def test_balance_is_non_zero_when_transfer_to_work_account_took_place(self) -> None:
        self.transfer_generator.create_transfer(debit_account=self.work_account)
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.account_balance


class WorkAccountTransferTests(InteractorTestBase):
    def test_no_transfers_returned_when_no_transfers_took_place(self) -> None:
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert not response.transfers

    def test_that_no_transfers_are_returned_when_account_owner_is_neither_debitor_nor_creditor_of_transfer(
        self,
    ) -> None:
        self.transfer_generator.create_transfer()
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert not response.transfers

    def test_that_transfer_is_returned_when_work_account_of_company_is_debit_account(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(debit_account=self.work_account)
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.transfers

    def test_that_transfer_is_returned_when_work_account_of_company_is_credit_account(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(credit_account=self.work_account)
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.transfers

    def test_that_transfers_to_other_accounts_of_company_do_not_show_up(self) -> None:
        self.transfer_generator.create_transfer(
            credit_account=self.company.means_account
        )
        self.transfer_generator.create_transfer(
            credit_account=self.company.raw_material_account
        )
        self.transfer_generator.create_transfer(
            credit_account=self.company.product_account
        )
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert not response.transfers

    def test_that_transfers_from_other_accounts_of_company_do_not_show_up(self) -> None:
        self.transfer_generator.create_transfer(
            debit_account=self.company.means_account
        )
        self.transfer_generator.create_transfer(
            debit_account=self.company.raw_material_account
        )
        self.transfer_generator.create_transfer(
            debit_account=self.company.product_account
        )
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert not response.transfers

    def test_two_transfers_are_recorded_in_descending_order(self) -> None:
        self.datetime_service.freeze_time(datetime_min_utc())
        self.transfer_generator.create_transfer(
            type=TransferType.work_certificates, credit_account=self.work_account
        )
        self.datetime_service.advance_time(timedelta(days=1))
        self.transfer_generator.create_transfer(
            type=TransferType.credit_a, credit_account=self.work_account
        )
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.transfers[0].type == TransferType.credit_a
        assert response.transfers[1].type == TransferType.work_certificates


class WorkAccountPlottingTests(InteractorTestBase):
    def test_that_plotting_info_is_empty_when_no_transfers_occurred(self) -> None:
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_transfer_took_place(
        self,
    ) -> None:
        self.transfer_generator.create_transfer(credit_account=self.work_account)
        response = self.interactor.show_details(
            self.create_interactor_request(self.company.id)
        )
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes
