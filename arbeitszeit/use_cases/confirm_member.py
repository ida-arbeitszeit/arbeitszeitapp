from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MemberRepository
from arbeitszeit.token import InvitationTokenValidator, TokenService


@inject
@dataclass
class ConfirmMemberUseCase:
    @dataclass
    class Request:
        member: UUID
        token: str

    @dataclass
    class Response:
        is_confirmed: bool = False

    member_repository: MemberRepository
    token_service: TokenService
    token_validator: InvitationTokenValidator

    def confirm_member(self, request: Request) -> Response:
        member = self.member_repository.get_by_id(request.member)
        if not member:
            return self.Response()
        unwrapped_token = self.token_validator.unwrap_invitation_token(request.token)
        if member.confirmed_on is None and member.email == unwrapped_token:
            self.member_repository.confirm_member(member.id, datetime.min)
            return self.Response(is_confirmed=True)
        return self.Response()
