from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
)
from arbeitszeit.token import CompanyRegistrationMessagePresenter, TokenService


@dataclass
class RegisterCompany:
    company_repository: CompanyRepository
    account_repository: AccountRepository
    member_repository: MemberRepository
    datetime_service: DatetimeService
    token_service: TokenService
    company_registration_message_presenter: CompanyRegistrationMessagePresenter
    password_hasher: PasswordHasher

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            company_already_exists = auto()
            user_password_is_invalid = auto()

        rejection_reason: Optional[RejectionReason]
        company_id: Optional[UUID]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    @dataclass
    class Request:
        email: str
        name: str
        password: str

    def register_company(self, request: Request) -> Response:
        try:
            company_id = self._register_company(request)
        except self.Response.RejectionReason as reason:
            return self.Response(rejection_reason=reason, company_id=None)
        return self.Response(rejection_reason=None, company_id=company_id)

    def _register_company(self, request: Request) -> UUID:
        if self.company_repository.get_companies().with_email_address(request.email):
            raise self.Response.RejectionReason.company_already_exists
        member = (
            self.member_repository.get_members()
            .with_email_address(request.email)
            .first()
        )
        if member:
            if not self.password_hasher.is_password_matching_hash(
                password=request.password, password_hash=member.password_hash
            ):
                raise self.Response.RejectionReason.user_password_is_invalid
        means_account = self.account_repository.create_account()
        resources_account = self.account_repository.create_account()
        labour_account = self.account_repository.create_account()
        products_account = self.account_repository.create_account()
        registered_on = self.datetime_service.now()
        company = self.company_repository.create_company(
            email=request.email,
            name=request.name,
            password_hash=self.password_hasher.calculate_password_hash(
                request.password
            ),
            means_account=means_account,
            labour_account=labour_account,
            resource_account=resources_account,
            products_account=products_account,
            registered_on=registered_on,
        )
        self._create_confirmation_mail(request, company.id)
        return company.id

    def _create_confirmation_mail(self, request: Request, company: UUID) -> None:
        token = self.token_service.generate_token(request.email)
        self.company_registration_message_presenter.show_company_registration_message(
            token=token, company=company
        )
