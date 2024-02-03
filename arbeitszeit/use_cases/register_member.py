from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import EmailSender, MemberRegistration
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RegisterMemberUseCase:
    datetime_service: DatetimeService
    email_sender: EmailSender
    password_hasher: PasswordHasher
    database: DatabaseGateway

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            member_already_exists = auto()
            company_with_different_password_exists = auto()

        rejection_reason: Optional[RejectionReason]
        user_id: Optional[UUID]
        is_confirmation_required: bool

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    @dataclass
    class Request:
        email: str
        name: str
        password: str
        repeat_password: str

    def register_member(self, request: Request) -> Response:
        try:
            return self._register_member(request)
        except RegisterMemberUseCase.Response.RejectionReason as reason:
            return RegisterMemberUseCase.Response(
                rejection_reason=reason, user_id=None, is_confirmation_required=False
            )

    def _register_member(self, request: Request) -> Response:
        credentials: records.AccountCredentials
        email_address: records.EmailAddress
        member: Optional[records.Member]
        record = (
            self.database.get_account_credentials()
            .with_email_address(request.email)
            .joined_with_email_address_and_member()
            .first()
        )
        if record is None:
            self.database.create_email_address(address=request.email, confirmed_on=None)
            credentials = self.database.create_account_credentials(
                password_hash=self.password_hasher.calculate_password_hash(
                    request.password
                ),
                email_address=request.email,
            )
            self._create_confirmation_mail(request.email)
        else:
            credentials, email_address, member = record
            if member:
                raise self.Response.RejectionReason.member_already_exists
            if not self.password_hasher.is_password_matching_hash(
                password=request.password,
                password_hash=credentials.password_hash,
            ):
                raise self.Response.RejectionReason.company_with_different_password_exists
        member_account = self.database.create_account()
        member = self.database.create_member(
            account_credentials=credentials.id,
            name=request.name,
            account=member_account,
            registered_on=self.datetime_service.now(),
        )
        return self.Response(
            rejection_reason=None,
            user_id=member.id,
            is_confirmation_required=not record,
        )

    def _create_confirmation_mail(self, email_address: str) -> None:
        self.email_sender.send_email(MemberRegistration(email_address=email_address))
