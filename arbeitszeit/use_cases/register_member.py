from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.presenters import MemberRegistrationMessagePresenter
from arbeitszeit.repositories import AccountRepository, DatabaseGateway


@dataclass
class RegisterMemberUseCase:
    account_repository: AccountRepository
    datetime_service: DatetimeService
    member_registration_message_presenter: MemberRegistrationMessagePresenter
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

    def register_member(self, request: Request) -> Response:
        try:
            return self._register_member(request)
        except RegisterMemberUseCase.Response.RejectionReason as reason:
            return RegisterMemberUseCase.Response(
                rejection_reason=reason, user_id=None, is_confirmation_required=False
            )

    def _register_member(self, request: Request) -> Response:
        if self.database.get_members().with_email_address(request.email):
            raise self.Response.RejectionReason.member_already_exists
        company = (
            self.database.get_companies().with_email_address(request.email).first()
        )
        if company:
            is_company_with_same_email_already_registered = True
            if not self.password_hasher.is_password_matching_hash(
                password=request.password,
                password_hash=company.password_hash,
            ):
                raise self.Response.RejectionReason.company_with_different_password_exists
        else:
            is_company_with_same_email_already_registered = False

        member_account = self.account_repository.create_account()
        registered_on = self.datetime_service.now()
        if not self.database.get_email_addresses().with_address(request.email):
            self.database.create_email_address(address=request.email, confirmed_on=None)
        member = self.database.create_member(
            email=request.email,
            name=request.name,
            password_hash=self.password_hasher.calculate_password_hash(
                request.password
            ),
            account=member_account,
            registered_on=registered_on,
        )
        if not is_company_with_same_email_already_registered:
            self._create_confirmation_mail(member.email)
        return self.Response(
            rejection_reason=None,
            user_id=member.id,
            is_confirmation_required=not is_company_with_same_email_already_registered,
        )

    def _create_confirmation_mail(self, email_address: str) -> None:
        self.member_registration_message_presenter.show_member_registration_message(
            email_address=email_address
        )
