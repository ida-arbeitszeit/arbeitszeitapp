from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import AccountTypes
from arbeitszeit.repositories import AccountRepository, MemberRepository
from arbeitszeit.token import ConfirmationEmail, TokenDeliverer, TokenService


@dataclass
class RegisterMemberResponse:
    class RejectionReason(Exception, Enum):
        member_already_exists = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RegisterMemberRequest:
    email: str
    name: str
    password: str


@inject
@dataclass
class RegisterMember:
    account_repository: AccountRepository
    member_repository: MemberRepository
    datetime_service: DatetimeService
    token_service: TokenService
    token_deliverer: TokenDeliverer

    def __call__(self, request: RegisterMemberRequest) -> RegisterMemberResponse:
        try:
            self._register_member(request)
        except RegisterMemberResponse.RejectionReason as reason:
            return RegisterMemberResponse(rejection_reason=reason)
        return RegisterMemberResponse(rejection_reason=None)

    def _register_member(self, request: RegisterMemberRequest) -> None:
        if self.member_repository.has_member_with_email(request.email):
            raise RegisterMemberResponse.RejectionReason.member_already_exists

        member_account = self.account_repository.create_account(AccountTypes.member)
        registered_on = self.datetime_service.now()
        self.member_repository.create_member(
            request.email, request.name, request.password, member_account, registered_on
        )
        self._create_confirmation_mail(request)

    def _create_confirmation_mail(self, request: RegisterMemberRequest) -> None:
        token = self.token_service.generate_token(request.email)
        self.token_deliverer.deliver_confirmation_token(
            ConfirmationEmail(token=token, email=request.email)
        )
