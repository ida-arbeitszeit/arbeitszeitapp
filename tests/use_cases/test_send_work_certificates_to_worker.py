from decimal import Decimal

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import update_plans_and_payout
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
        self.update_plans_and_payout = self.injector.get(
            update_plans_and_payout.UpdatePlansAndPayout
        )

    def test_that_request_is_rejected_if_worker_is_not_member_of_company(
        self,
    ) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker1])
        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker2, hours_worked=Decimal(50)
            )
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == SendWorkCertificatesToWorkerResponse.RejectionReason.worker_not_at_company
        )

    def test_that_requrest_is_granted_when_worker_is_member_of_company(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker])
        amount_to_transfer = Decimal(50)
        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker, hours_worked=amount_to_transfer
            )
        )
        assert not response.is_rejected

    def test_with_no_public_plans_that_certificates_received_equal_hours_worked(
        self,
    ) -> None:
        worker = self.member_generator.create_member_entity()
        company = self.company_generator.create_company_entity(workers=[worker.id])
        hours_worked = Decimal(50)
        self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker.id, hours_worked=hours_worked
            )
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )
        assert (
            self.balance_checker.get_member_account_balance(worker.id) == hours_worked
        )

    def test_that_request_with_negative_hours_worked_is_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker])
        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker, hours_worked=Decimal("-1")
            )
        )
        assert response.is_rejected

    def test_that_request_with_zero_hours_worked_is_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker])
        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker, hours_worked=Decimal("0")
            )
        )
        assert response.is_rejected

    def test_that_request_with_zero_hours_worked_is_rejected_for_the_right_reason(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[worker])
        response = self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker, hours_worked=Decimal("0")
            )
        )
        assert (
            response.rejection_reason
            == SendWorkCertificatesToWorkerResponse.RejectionReason.hours_worked_must_be_positive
        )

    def test_that_with_all_public_plans_that_worker_receives_no_certificates(
        self,
    ) -> None:
        worker = self.member_generator.create_member_entity()
        company = self.company_generator.create_company_entity(workers=[worker.id])
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        self.update_plans_and_payout()
        hours_worked = Decimal(10)
        self.send_work_certificates_to_worker(
            SendWorkCertificatesToWorkerRequest(
                company.id, worker.id, hours_worked=hours_worked
            )
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )
        assert self.balance_checker.get_member_account_balance(worker.id) == Decimal(
            "0"
        )
