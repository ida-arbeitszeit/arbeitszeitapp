from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import CoordinationTransferRequest
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class AcceptCoordinationTransferUseCase:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    @dataclass
    class Request:
        transfer_request_id: UUID

    @dataclass
    class Response:
        @dataclass
        class RejectionReason(Exception, Enum):
            transfer_request_not_found = auto()
            transfer_request_closed = auto()

        rejection_reason: Optional[RejectionReason]
        cooperation_id: Optional[UUID]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    def accept_coordination_transfer(self, request: Request) -> Response:
        try:
            transfer_request = self._validate_request(request)
        except self.Response.RejectionReason as reason:
            return self.Response(rejection_reason=reason, cooperation_id=None)
        self._close_transfer_request(request)
        cooperation = self._create_new_coordination_tenure(transfer_request)
        return self.Response(rejection_reason=None, cooperation_id=cooperation)

    def _validate_request(self, request: Request) -> CoordinationTransferRequest:
        transfer_request = (
            self.database_gateway.get_coordination_transfer_requests()
            .with_id(request.transfer_request_id)
            .first()
        )
        if transfer_request is None:
            raise self.Response.RejectionReason.transfer_request_not_found
        if not transfer_request.is_open():
            raise self.Response.RejectionReason.transfer_request_closed
        return transfer_request

    def _close_transfer_request(self, request: Request) -> None:
        transfer_date = self.datetime_service.now()
        self.database_gateway.get_coordination_transfer_requests().with_id(
            request.transfer_request_id
        ).update().set_transfer_date(transfer_date).perform()

    def _create_new_coordination_tenure(
        self, transfer_request: CoordinationTransferRequest
    ) -> UUID:
        old_tenure = (
            self.database_gateway.get_coordination_tenures()
            .with_id(transfer_request.requesting_coordination_tenure)
            .first()
        )
        assert old_tenure
        new_tenure = self.database_gateway.create_coordination_tenure(
            company=transfer_request.candidate,
            cooperation=old_tenure.cooperation,
            start_date=self.datetime_service.now(),
        )
        return new_tenure.cooperation
