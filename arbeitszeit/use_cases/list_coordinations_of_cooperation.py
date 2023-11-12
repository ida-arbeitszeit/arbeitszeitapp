from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class CoordinationInfo:
    coordinator_id: UUID
    coordinator_name: str
    start_time: datetime
    end_time: Optional[datetime]


@dataclass
class ListCoordinationsOfCooperationUseCase:
    database_gateway: DatabaseGateway

    @dataclass
    class Request:
        cooperation: UUID

    @dataclass
    class Response:
        coordinations: list[CoordinationInfo]
        cooperation_id: UUID
        cooperation_name: str

    def list_coordinations(self, request: Request) -> Response:
        tenures_and_coordinators = list(
            self.database_gateway.get_coordination_tenures()
            .of_cooperation(request.cooperation)
            .ordered_by_start_date(ascending=False)
            .joined_with_coordinator()
        )
        coordinations: list[CoordinationInfo] = []
        end_timestamp = None
        for tenure, coordinator in tenures_and_coordinators:
            coordinations.append(
                CoordinationInfo(
                    coordinator_id=coordinator.id,
                    coordinator_name=coordinator.name,
                    start_time=tenure.start_date,
                    end_time=end_timestamp,
                )
            )
        assert coordinations  # there cannot be a cooperation without at least one coordination_tenure
        cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(request.cooperation)
            .first()
        )
        assert cooperation

        return self.Response(
            coordinations=coordinations,
            cooperation_id=request.cooperation,
            cooperation_name=cooperation.name,
        )
