from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    requester: UUID
    registration_id: UUID


@dataclass
class Response:
    delete_succeeded: bool


@dataclass
class CancelHoursWorkedUseCase:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def cancel_hours_worked(self, request: Request) -> Response:
        requester = self.database.get_companies().with_id(request.requester).first()
        query_result = self.database.get_registered_hours_worked().with_id(
            request.registration_id
        )
        row_to_be_deleted = query_result.first()
        if not requester or not row_to_be_deleted:
            return Response(delete_succeeded=False)
        if requester.id != row_to_be_deleted.company:
            return Response(delete_succeeded=False)
        query_result.delete()
        return Response(delete_succeeded=True)
