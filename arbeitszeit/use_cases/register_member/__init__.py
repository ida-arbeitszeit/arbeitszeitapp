from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import AccountTypes
from arbeitszeit.repositories import AccountRepository, MemberRepository
from arbeitszeit.token import MemberRegistrationMessagePresenter, TokenService


@inject
@dataclass
class RegisterMemberUseCase:
    account_repository: AccountRepository
    member_repository: MemberRepository
    datetime_service: DatetimeService
    token_service: TokenService
    member_registration_message_presenter: MemberRegistrationMessagePresenter

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            member_already_exists = auto()

        rejection_reason: Optional[RejectionReason]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    @dataclass
    class Request:
        email: str
        name: str
        password: str

    def register_member(self, request: Request) -> Response:
        try:
            self._register_member(request)
        except RegisterMemberUseCase.Response.RejectionReason as reason:
            return RegisterMemberUseCase.Response(rejection_reason=reason)
        return RegisterMemberUseCase.Response(rejection_reason=None)

    def _register_member(self, request: Request) -> None:
        if self.member_repository.has_member_with_email(request.email):
            raise self.Response.RejectionReason.member_already_exists

        member_account = self.account_repository.create_account(AccountTypes.member)
        registered_on = self.datetime_service.now()
        member = self.member_repository.create_member(
            request.email, request.name, request.password, member_account, registered_on
        )
        self._create_confirmation_mail(request, member.id)

    def _create_confirmation_mail(self, request: Request, member: UUID) -> None:
        token = self.token_service.generate_token(request.email)
        self.member_registration_message_presenter.show_member_registration_message(
            token=token, member=member
        )
