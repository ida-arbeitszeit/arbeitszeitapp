from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from arbeitszeit.records import Cooperation, CoordinationTransferRequest
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class GetCoordinationTransferRequestDetailsUseCase:
    @dataclass
    class Request:
        coordination_transfer_request: UUID

    @dataclass
    class Response:
        request_date: datetime
        cooperation_id: UUID
        cooperation_name: str
        candidate_id: UUID
        candidate_name: str
        request_is_pending: bool

    database_gateway: DatabaseGateway

    def get_details(self, request: Request) -> Optional[Response]:
        transfer_request_and_cooperation = (
            self.database_gateway.get_coordination_transfer_requests()
            .with_id(request.coordination_transfer_request)
            .joined_with_cooperation()
            .first()
        )
        if not transfer_request_and_cooperation:
            return None
        transfer_request, cooperation = transfer_request_and_cooperation
        candidate = (
            self.database_gateway.get_companies()
            .with_id(transfer_request.candidate)
            .first()
        )
        assert candidate
        return self.Response(
            request_date=transfer_request.request_date,
            cooperation_id=cooperation.id,
            cooperation_name=cooperation.name,
            candidate_id=transfer_request.candidate,
            candidate_name=candidate.name,
            request_is_pending=not self._cooperation_has_a_coordination_tenure_starting_after_transfer_request(
                transfer_request=transfer_request, cooperation=cooperation
            ),
        )

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
