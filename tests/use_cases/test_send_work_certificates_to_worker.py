from decimal import Decimal

from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorker,
    SendWorkCertificatesToWorkerRequest,
    SendWorkCertificatesToWorkerResponse,
)

from .base_test_case import BaseTestCase
from .repositories import EntityStorage


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.send_work_certificates_to_worker = self.injector.get(
            SendWorkCertificatesToWorker
        )
        self.entity_storage = self.injector.get(EntityStorage)

    def test_that_transfer_is_rejected_if_money_is_sent_to_worker_not_working_in_company(
        self,
    ) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker1])
        amount_to_transfer = Decimal(50)

        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(company.id, worker2, amount_to_transfer)
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == SendWorkCertificatesToWorkerResponse.RejectionReason.worker_not_at_company
        )

    def test_that_correct_transfer_does_not_get_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker])
        amount_to_transfer = Decimal(50)
        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(company.id, worker, amount_to_transfer)
        )
        assert not response.is_rejected

    def test_that_after_transfer_balances_of_worker_and_company_are_correct(
        self,
    ) -> None:
        worker = self.member_generator.create_member_entity()
        company = self.company_generator.create_company_entity(workers=[worker.id])
        amount_to_transfer = Decimal(50)
        self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker.id, amount_to_transfer
            )
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -amount_to_transfer
        )
        assert (
            self.balance_checker.get_member_account_balance(worker.id)
            == amount_to_transfer
        )

    def test_that_after_transfer_one_transaction_is_added(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker])
        amount_to_transfer = Decimal(50)
        self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(company.id, worker, amount_to_transfer)
        )
        assert len(self.entity_storage.get_transactions()) == 1

    def test_that_after_transfer_correct_transaction_is_added(self) -> None:
        worker = self.member_generator.create_member_entity()
        company = self.company_generator.create_company_entity(workers=[worker.id])
        amount_to_transfer = Decimal(50)
        self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker.id, amount_to_transfer
            )
        )

        assert len(self.entity_storage.get_transactions()) == 1
        transaction = self.entity_storage.get_transactions().first()
        assert transaction
        assert transaction.amount_sent == amount_to_transfer
        assert transaction.amount_received == amount_to_transfer
        assert transaction.sending_account == company.work_account
        assert transaction.receiving_account == worker.account
