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
            self.database_gateway.get_registered_hours_worked()
            .at_company(request.company_id)
            .ordered_by_registration_time(is_ascending=False)
            .joined_with_worker()
        )
        registered_hours_worked = [
            RegisteredHoursWorked(
                hours=registered_hours.amount,
                worker_id=registered_hours.member,
                worker_name=worker.get_name(),
                registered_on=registered_hours.registered_on,
            )
            for registered_hours, worker in records
        ]
        return Response(registered_hours_worked=registered_hours_worked)
