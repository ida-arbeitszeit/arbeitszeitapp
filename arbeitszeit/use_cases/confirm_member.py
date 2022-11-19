from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MemberRepository
from arbeitszeit.token import InvitationTokenValidator, TokenService


@inject
@dataclass
class ConfirmMemberUseCase:
    @dataclass
    class Request:
        token: str

    @dataclass
    class Response:
        is_confirmed: bool
        member: Optional[UUID] = None

    member_repository: MemberRepository
    token_service: TokenService
    token_validator: InvitationTokenValidator

    def confirm_member(self, request: Request) -> Response:
        unwrapped_token = self.token_validator.unwrap_confirmation_token(request.token)
        if unwrapped_token:
            member = (
                self.member_repository.get_members()
                .with_email_address(unwrapped_token)
                .first()
            )
            if not member:
                return self.Response(is_confirmed=False)
            if member.confirmed_on is None:
                self.member_repository.confirm_member(member.id, datetime.min)
                return self.Response(is_confirmed=True, member=member.id)
        return self.Response(is_confirmed=False)
