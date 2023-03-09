from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import MemberRepository
from arbeitszeit.token import InvitationTokenValidator, TokenService


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
            members = self.member_repository.get_members().with_email_address(
                unwrapped_token
            )
            if not members:
                return self.Response(is_confirmed=False)
            if members.that_are_confirmed():
                pass
            else:
                members.update().set_confirmation_timestamp(datetime.min).perform()
                member = members.first()
                assert member
                return self.Response(is_confirmed=True, member=member.id)
        return self.Response(is_confirmed=False)
