from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    TransactionRepository,
)


@dataclass
class SendWorkCertificatesToWorkerRequest:
    company_id: UUID
    worker_id: UUID
    amount: Decimal


@dataclass
class SendWorkCertificatesToWorkerResponse:
    class RejectionReason(Exception, Enum):
        worker_not_at_company = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class SendWorkCertificatesToWorker:
    company_repository: CompanyRepository
    member_repository: MemberRepository
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService

    def __call__(
        self, use_case_request: SendWorkCertificatesToWorkerRequest
    ) -> SendWorkCertificatesToWorkerResponse:
        company = self.company_repository.get_by_id(use_case_request.company_id)
        worker = (
            self.member_repository.get_members()
            .with_id(use_case_request.worker_id)
            .first()
        )
        assert company
        assert worker
        company_workers = self.member_repository.get_members().working_at_company(
            company.id
        )
        if worker not in company_workers:
            return SendWorkCertificatesToWorkerResponse(
                rejection_reason=SendWorkCertificatesToWorkerResponse.RejectionReason.worker_not_at_company
            )
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=company.work_account,
            receiving_account=worker.account,
            amount_sent=use_case_request.amount,
            amount_received=use_case_request.amount,
            purpose="Lohn",
        )
        return SendWorkCertificatesToWorkerResponse(rejection_reason=None)
