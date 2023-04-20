from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
)
from arbeitszeit.token import MemberRegistrationMessagePresenter, TokenService


@dataclass
class RegisterMemberUseCase:
    account_repository: AccountRepository
    member_repository: MemberRepository
    datetime_service: DatetimeService
    token_service: TokenService
    member_registration_message_presenter: MemberRegistrationMessagePresenter
    company_repository: CompanyRepository

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

    def register_member(self, request: Request) -> Response:
        try:
            return self._register_member(request)
        except RegisterMemberUseCase.Response.RejectionReason as reason:
            return RegisterMemberUseCase.Response(
                rejection_reason=reason, user_id=None, is_confirmation_required=False
            )

    def _register_member(self, request: Request) -> Response:
        if self.member_repository.get_members().with_email_address(request.email):
            raise self.Response.RejectionReason.member_already_exists
        if self.company_repository.get_companies().with_email_address(request.email):
            is_company_with_same_email_already_registered = True
            if not self.company_repository.validate_credentials(
                request.email, request.password
            ):
                raise self.Response.RejectionReason.company_with_different_password_exists
        else:
            is_company_with_same_email_already_registered = False

        member_account = self.account_repository.create_account()
        registered_on = self.datetime_service.now()
        member = self.member_repository.create_member(
            email=request.email,
            name=request.name,
            password=request.password,
            account=member_account,
            registered_on=registered_on,
        )
        if not is_company_with_same_email_already_registered:
            self._create_confirmation_mail(request, member.id)
        return self.Response(
            rejection_reason=None,
            user_id=member.id,
            is_confirmation_required=not is_company_with_same_email_already_registered,
        )

    def _create_confirmation_mail(self, request: Request, member: UUID) -> None:
        token = self.token_service.generate_token(request.email)
        self.member_registration_message_presenter.show_member_registration_message(
            token=token, member=member
        )
