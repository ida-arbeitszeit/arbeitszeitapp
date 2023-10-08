from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class CoordinationInfo:
    coordinator_id: UUID
    coordinator_name: str
    start_time: datetime


@dataclass
class ListCoordinationsOfCooperationUseCase:
    database_gateway: DatabaseGateway

    @dataclass
    class Request:
        cooperation: UUID

    @dataclass
    class Response:
        coordinations: list[CoordinationInfo]

    def list_coordinations(self, request: Request) -> Response:
        tenure_and_coordinator = (
            self.database_gateway.get_coordination_tenures()
            .of_cooperation(request.cooperation)
            .joined_with_coordinator()
        )
        coordinations: list[CoordinationInfo] = []
        for tenure, coordinator in tenure_and_coordinator:
            info = CoordinationInfo(
                coordinator_id=coordinator.id,
                coordinator_name=coordinator.name,
                start_time=tenure.start_date,
            )
            coordinations.append(info)
        assert coordinations  # there cannot be a cooperation without at least one coordination_tenure
        return self.Response(coordinations=coordinations)
