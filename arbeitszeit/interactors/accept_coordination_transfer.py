from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Cooperation, CoordinationTransferRequest
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class AcceptCoordinationTransferInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    @dataclass
    class Request:
        transfer_request_id: UUID
        accepting_company: UUID

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            transfer_request_not_found = auto()
            transfer_request_closed = auto()
            accepting_company_is_not_candidate = auto()

        rejection_reason: Optional[RejectionReason]
        cooperation_id: Optional[UUID]
        transfer_request_id: UUID

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    def accept_coordination_transfer(self, request: Request) -> Response:
        try:
            transfer_request, cooperation = self._validate_request(request)
        except self.Response.RejectionReason as reason:
            return self.Response(
                rejection_reason=reason,
                cooperation_id=None,
                transfer_request_id=request.transfer_request_id,
            )
        cooperation_id = self._create_new_coordination_tenure(
            transfer_request, cooperation
        )
        return self.Response(
            rejection_reason=None,
            cooperation_id=cooperation_id,
            transfer_request_id=request.transfer_request_id,
        )

    def _validate_request(
        self, request: Request
    ) -> tuple[CoordinationTransferRequest, Cooperation]:
        result = (
            self.database_gateway.get_coordination_transfer_requests()
            .with_id(request.transfer_request_id)
            .joined_with_cooperation()
            .first()
        )
        if result is None:
            raise self.Response.RejectionReason.transfer_request_not_found
        transfer_request, cooperation = result
        if transfer_request.candidate != request.accepting_company:
            raise self.Response.RejectionReason.accepting_company_is_not_candidate
        if self._cooperation_has_a_coordination_tenure_starting_after_transfer_request(
            cooperation=cooperation, transfer_request=transfer_request
        ):
            raise self.Response.RejectionReason.transfer_request_closed
        return transfer_request, cooperation

    def _create_new_coordination_tenure(
        self, transfer_request: CoordinationTransferRequest, cooperation: Cooperation
    ) -> UUID:
        new_tenure = self.database_gateway.create_coordination_tenure(
            company=transfer_request.candidate,
            cooperation=cooperation.id,
            start_date=self.datetime_service.now(),
        )
        return new_tenure.cooperation

    def _cooperation_has_a_coordination_tenure_starting_after_transfer_request(
        self, transfer_request: CoordinationTransferRequest, cooperation: Cooperation
    ) -> bool:
        latest_coordination_tenure_of_cooperation = (
            self.database_gateway.get_coordination_tenures()
            .of_cooperation(cooperation.id)
            .ordered_by_start_date(ascending=False)
            .first()
        )
        assert latest_coordination_tenure_of_cooperation
        return (
            latest_coordination_tenure_of_cooperation.start_date
            > transfer_request.request_date
        )
