from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union
from uuid import UUID

from arbeitszeit import entities
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class GetUserAccountDetailsUseCase:
    database: DatabaseGateway

    def get_user_account_details(self, request: Request) -> Response:
        user: Union[entities.Member, entities.Company, entities.Accountant, None] = (
            self.database.get_members().with_id(request.user_id).first()
            or self.database.get_companies().with_id(request.user_id).first()
            or self.database.get_accountants().with_id(request.user_id).first()
        )
        return Response(
            user_info=UserInfo(id=user.id, email_address=user.email_address)
            if user
            else None
        )


@dataclass
class Request:
    user_id: UUID


@dataclass
class Response:
    user_info: Optional[UserInfo]


@dataclass
class UserInfo:
    id: UUID
    email_address: str
