from dataclasses import dataclass
from decimal import Decimal
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
        nr_of_deleted_rows = query_result.delete()
        assert nr_of_deleted_rows == 1

        undone_transaction = (
            self.database.get_transactions()
            .with_id(row_to_be_deleted.transaction)
            .first()
        )
        assert undone_transaction
        now = self.datetime_service.now()
        self.database.create_transaction(
            date=now,
            sending_account=undone_transaction.sending_account,
            receiving_account=undone_transaction.receiving_account,
            amount_sent=undone_transaction.amount_sent * Decimal(-1),
            amount_received=undone_transaction.amount_received * Decimal(-1),
            purpose="Storno",
        )

        return Response(delete_succeeded=True)
