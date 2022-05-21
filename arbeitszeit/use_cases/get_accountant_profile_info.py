from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import AccountantRepository


@dataclass
class GetAccountantProfileInfoUseCase:
    @dataclass
    class Request:
        user_id: UUID

    @dataclass
    class Record:
        email_address: str
        name: str

    @dataclass
    class Response:
        record: Optional[GetAccountantProfileInfoUseCase.Record]

    accountant_repository: AccountantRepository

    def get_accountant_profile_info(self, request: Request) -> Response:
        accountant = self.accountant_repository.get_by_id(request.user_id)
        if accountant is None:
            return self.Response(record=None)
        record = self.Record(
            email_address=accountant.email_address, name=accountant.name
        )
        return self.Response(record=record)
