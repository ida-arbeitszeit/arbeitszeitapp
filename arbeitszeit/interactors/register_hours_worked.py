from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import SocialAccounting
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.payout_factor import PayoutFactorService
from arbeitszeit.transfers import TransferType


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

    rejection_reason: RejectionReason | None
    registered_hours_worked_id: UUID | None

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RegisterHoursWorkedInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    fic_service: PayoutFactorService
    social_accounting: SocialAccounting

    def execute(
        self, interactor_request: RegisterHoursWorkedRequest
    ) -> RegisterHoursWorkedResponse:
        if interactor_request.hours_worked <= Decimal(0):
            return RegisterHoursWorkedResponse(
                rejection_reason=RegisterHoursWorkedResponse.RejectionReason.hours_worked_must_be_positive,
                registered_hours_worked_id=None,
            )
        company = (
            self.database_gateway.get_companies()
            .with_id(interactor_request.company_id)
            .first()
        )
        worker = (
            self.database_gateway.get_members()
            .with_id(interactor_request.worker_id)
            .first()
        )
        assert company
        assert worker
        company_workers = self.database_gateway.get_members().working_at_company(
            company.id
        )
        if worker not in company_workers:
            return RegisterHoursWorkedResponse(
                rejection_reason=RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company,
                registered_hours_worked_id=None,
            )
        fic = self.fic_service.calculate_current_payout_factor()
        transfer_of_work_certificates = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=company.work_account,
            credit_account=worker.account,
            value=interactor_request.hours_worked,
            type=TransferType.work_certificates,
        )
        transfer_of_taxes = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=worker.account,
            credit_account=self.social_accounting.account_psf,
            value=interactor_request.hours_worked * (1 - fic),
            type=TransferType.taxes,
        )
        registered_hours_worked = self.database_gateway.create_registered_hours_worked(
            company=company.id,
            member=worker.id,
            transfer_of_work_certificates=transfer_of_work_certificates.id,
            transfer_of_taxes=transfer_of_taxes.id,
            registered_on=self.datetime_service.now(),
        )
        return RegisterHoursWorkedResponse(
            rejection_reason=None, registered_hours_worked_id=registered_hours_worked.id
        )
