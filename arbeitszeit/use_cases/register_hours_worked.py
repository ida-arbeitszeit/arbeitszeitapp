from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RegisterHoursWorkedRequest:
    company_id: UUID
    worker_id: UUID
    hours_worked: Decimal


@dataclass
class RegisterHoursWorkedResponse:
    class RejectionReason(Exception, Enum):
        worker_not_at_company = auto()
        hours_worked_must_be_positive = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RegisterHoursWorked:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    fic_service: PayoutFactorService

    def __call__(
        self, use_case_request: RegisterHoursWorkedRequest
    ) -> RegisterHoursWorkedResponse:
        if use_case_request.hours_worked <= Decimal(0):
            return RegisterHoursWorkedResponse(
                rejection_reason=RegisterHoursWorkedResponse.RejectionReason.hours_worked_must_be_positive
            )
        company = (
            self.database_gateway.get_companies()
            .with_id(use_case_request.company_id)
            .first()
        )
        worker = (
            self.database_gateway.get_members()
            .with_id(use_case_request.worker_id)
            .first()
        )
        assert company
        assert worker
        company_workers = self.database_gateway.get_members().working_at_company(
            company.id
        )
        if worker not in company_workers:
            return RegisterHoursWorkedResponse(
                rejection_reason=RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company
            )
        fic = self.fic_service.get_current_payout_factor()
        now = self.datetime_service.now()
        transaction = self.database_gateway.create_transaction(
            date=now,
            sending_account=company.work_account,
            receiving_account=worker.account,
            amount_sent=use_case_request.hours_worked,
            amount_received=use_case_request.hours_worked * fic,
            purpose="Lohn",
        )
        self.database_gateway.create_registered_hours_worked(
            company=company.id,
            member=worker.id,
            amount=use_case_request.hours_worked,
            transaction=transaction.id,
            registered_on=now,
        )
        return RegisterHoursWorkedResponse(rejection_reason=None)
