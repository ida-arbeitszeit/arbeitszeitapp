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
        requester: UUID
        cooperation: UUID
        candidate: UUID

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            candidate_is_not_a_company = auto()
            requester_is_not_coordinator = auto()
            candidate_is_current_coordinator = auto()
            coordination_tenure_has_pending_transfer_request = auto()
            cooperation_not_found = auto()

        rejection_reason: Optional[RejectionReason]
        transfer_request: Optional[UUID]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    def request_transfer(self, request: Request) -> Response:
        try:
            candidate, candidate_email, coordination_tenure = self._validate_request(
                request
            )
        except self.Response.RejectionReason as reason:
            return self.Response(
                rejection_reason=reason,
                transfer_request=None,
            )
        transfer_request = self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=coordination_tenure.id,
            candidate=request.candidate,
            request_date=self.datetime_service.now(),
        )
        cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(coordination_tenure.cooperation)
            .first()
        )
        assert cooperation
        self.email_sender.send_email(
            CoordinationTransferRequest(
                candidate_name=candidate.name,
                candidate_email=candidate_email.address,
                cooperation_name=cooperation.name,
                transfer_request=transfer_request.id,
            )
        )
        return self.Response(
            rejection_reason=None,
            transfer_request=transfer_request.id,
        )

    def _validate_request(
        self, request: Request
    ) -> tuple[Company, EmailAddress, CoordinationTenure]:
        candidate_record = (
            self.database_gateway.get_companies()
            .with_id(request.candidate)
            .joined_with_email_address()
            .first()
        )
        if not candidate_record:
            raise self.Response.RejectionReason.candidate_is_not_a_company
        candidate, candidate_email = candidate_record

        coordination_tenures_and_coordinators = list(
            self.database_gateway.get_coordination_tenures()
            .of_cooperation(request.cooperation)
            .ordered_by_start_date(ascending=False)
            .joined_with_coordinator()
        )
        if not coordination_tenures_and_coordinators:
            raise self.Response.RejectionReason.cooperation_not_found

        latest_coordination_tenure_and_coordinator = (
            coordination_tenures_and_coordinators[0]
        )

        coordination_tenure, coordinator = latest_coordination_tenure_and_coordinator
        if coordinator.id != request.requester:
            raise self.Response.RejectionReason.requester_is_not_coordinator
        if coordination_tenure.company == candidate.id:
            raise self.Response.RejectionReason.candidate_is_current_coordinator
        if self._there_is_a_pending_transfer_request_by_coordination_tenure(
            coordination_tenure
        ):
            raise self.Response.RejectionReason.coordination_tenure_has_pending_transfer_request
        return candidate, candidate_email, coordination_tenure

    def _there_is_a_pending_transfer_request_by_coordination_tenure(
        self, coordination_tenure: CoordinationTenure
    ) -> bool:
        return bool(
            self.database_gateway.get_coordination_transfer_requests().requested_by(
                coordination_tenure.id
            )
        )
