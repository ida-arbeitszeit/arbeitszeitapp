from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import CoordinationTransferRequest, EmailSender
from arbeitszeit.records import Company, CoordinationTenure, EmailAddress
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RequestCoordinationTransferUseCase:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    email_sender: EmailSender

    @dataclass
    class Request:
        requesting_coordination_tenure: UUID
        candidate: UUID

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            candidate_is_not_a_company = auto()
            requesting_tenure_not_found = auto()
            candidate_is_current_coordinator = auto()
            requesting_tenure_is_not_current_tenure = auto()
            requesting_tenure_has_open_transfer_request = auto()

        rejection_reason: Optional[RejectionReason]
        transfer_request: Optional[UUID]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    def request_transfer(self, request: Request) -> Response:
        try:
            candidate, candidate_email, requesting_tenure = self._validate_request(
                request
            )
        except self.Response.RejectionReason as reason:
            return self.Response(rejection_reason=reason, transfer_request=None)
        transfer_request = self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=request.requesting_coordination_tenure,
            candidate=request.candidate,
            request_date=self.datetime_service.now(),
        )
        cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(requesting_tenure.cooperation)
            .first()
        )
        assert cooperation
        self.email_sender.send_email(
            CoordinationTransferRequest(
                candidate_name=candidate.name,
                candidate_email=candidate_email.address,
                cooperation_id=cooperation.id,
                cooperation_name=cooperation.name,
            )
        )
        return self.Response(
            rejection_reason=None, transfer_request=transfer_request.id
        )

    def _validate_request(
        self, request: Request
    ) -> tuple[Company, EmailAddress, CoordinationTenure]:
        record = (
            self.database_gateway.get_companies()
            .with_id(request.candidate)
            .joined_with_email_address()
            .first()
        )
        if not record:
            raise self.Response.RejectionReason.candidate_is_not_a_company
        candidate, candidate_email = record
        requesting_tenure = (
            self.database_gateway.get_coordination_tenures()
            .with_id(request.requesting_coordination_tenure)
            .first()
        )
        if not requesting_tenure:
            raise self.Response.RejectionReason.requesting_tenure_not_found
        if requesting_tenure.company == candidate.id:
            raise self.Response.RejectionReason.candidate_is_current_coordinator
        if not self._requesting_coordination_tenure_is_current(requesting_tenure):
            raise self.Response.RejectionReason.requesting_tenure_is_not_current_tenure
        if self._requesting_tenure_has_open_transfer_request(requesting_tenure):
            raise self.Response.RejectionReason.requesting_tenure_has_open_transfer_request
        return candidate, candidate_email, requesting_tenure

    def _requesting_coordination_tenure_is_current(
        self, requesting_tenure: CoordinationTenure
    ) -> bool:
        latest_tenure = (
            self.database_gateway.get_coordination_tenures()
            .of_cooperation(requesting_tenure.cooperation)
            .ordered_by_start_date(ascending=False)
            .first()
        )
        assert latest_tenure
        if requesting_tenure.id == latest_tenure.id:
            return True
        return False

    def _requesting_tenure_has_open_transfer_request(
        self, requesting_tenure: CoordinationTenure
    ) -> bool:
        transfer_requests = (
            self.database_gateway.get_coordination_transfer_requests()
            .requested_by(requesting_tenure.id)
            .that_are_open()
        )
        return len(transfer_requests) > 0
