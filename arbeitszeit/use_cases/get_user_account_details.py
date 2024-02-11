from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, Union
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class GetUserAccountDetailsUseCase:
    database: DatabaseGateway

    def get_user_account_details(self, request: Request) -> Response:
        record: Optional[
            Tuple[
                Union[records.Member, records.Company, records.Accountant],
                records.EmailAddress,
            ],
        ] = (
            (
                self.database.get_members().with_id(request.user_id)
                or self.database.get_companies().with_id(request.user_id)
                or self.database.get_accountants().with_id(request.user_id)
            )
            .joined_with_email_address()
            .first()
        )
        if not record:
            return self._create_failure_model()
        else:
            user, mail = record
            return self._create_success_model(user.id, mail)

    def _create_success_model(
        self, user_id: UUID, email_address: records.EmailAddress
    ) -> Response:
        return Response(
            user_info=UserInfo(
                id=user_id,
                email_address=email_address.address,
                email_address_confirmation_timestamp=email_address.confirmed_on,
            )
        )

    def _create_failure_model(self) -> Response:
        return Response(user_info=None)


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
    email_address_confirmation_timestamp: Optional[datetime] = None
