from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import AccountTypes
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    company_id: UUID


@dataclass
class RegisteredHoursWorked:
    hours: Decimal
    worker_id: UUID
    worker_name: str
    registered_on: datetime


@dataclass
class Response:
    registered_hours_worked: list[RegisteredHoursWorked]


@dataclass
class ListRegisteredHoursWorkedUseCase:
    database_gateway: DatabaseGateway

    def list_registered_hours_worked(self, request: Request) -> Response:
        company = (
            self.database_gateway.get_companies().with_id(request.company_id).first()
        )
        assert company
        work_account = company.get_account_by_type(AccountTypes.a)
        assert work_account
        records = (
            self.database_gateway.get_transactions()
            .where_account_is_sender(work_account)
            .ordered_by_transaction_date(descending=True)
            .joined_with_receiver()
        )
        registered_hours_worked = [
            RegisteredHoursWorked(
                hours=transaction.amount_sent,
                worker_id=worker.id,
                worker_name=worker.get_name(),
                registered_on=transaction.date,
            )
            for transaction, worker in records
        ]
        return Response(registered_hours_worked=registered_hours_worked)
