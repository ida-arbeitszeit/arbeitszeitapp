from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
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
        if (
            payout_factor := self.database_gateway.get_payout_factors()
            .ordered_by_calculation_date(descending=True)
            .first()
        ):
            fik = payout_factor.value
        else:
            fik = Decimal(1)
        self.database_gateway.create_transaction(
            date=self.datetime_service.now(),
            sending_account=company.work_account,
            receiving_account=worker.account,
            amount_sent=use_case_request.hours_worked,
            amount_received=use_case_request.hours_worked * fik,
            purpose="Lohn",
        )
        return RegisterHoursWorkedResponse(rejection_reason=None)
