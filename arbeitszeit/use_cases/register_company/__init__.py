from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import AccountTypes
from arbeitszeit.repositories import AccountRepository, CompanyRepository
from arbeitszeit.token import TokenService

from .company_registration_message_presenter import CompanyRegistrationMessagePresenter


@inject
@dataclass
class RegisterCompany:
    company_repository: CompanyRepository
    account_repository: AccountRepository
    datetime_service: DatetimeService
    token_service: TokenService
    company_registration_message_presenter: CompanyRegistrationMessagePresenter

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            company_already_exists = auto()

        rejection_reason: Optional[RejectionReason]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    @dataclass
    class Request:
        email: str
        name: str
        password: str

    def __call__(self, request: Request) -> Response:
        try:
            self._register_company(request)
        except self.Response.RejectionReason as reason:
            return self.Response(rejection_reason=reason)
        return self.Response(rejection_reason=None)

    def _register_company(self, request: Request) -> None:
        if self.company_repository.has_company_with_email(request.email):
            raise self.Response.RejectionReason.company_already_exists
        means_account = self.account_repository.create_account(AccountTypes.p)
        resources_account = self.account_repository.create_account(AccountTypes.r)
        labour_account = self.account_repository.create_account(AccountTypes.a)
        products_account = self.account_repository.create_account(AccountTypes.prd)
        registered_on = self.datetime_service.now()
        company = self.company_repository.create_company(
            request.email,
            request.name,
            request.password,
            means_account,
            labour_account,
            resources_account,
            products_account,
            registered_on,
        )
        self._create_confirmation_mail(request, company.id)

    def _create_confirmation_mail(self, request: Request, company: UUID) -> None:
        token = self.token_service.generate_token(request.email)
        self.company_registration_message_presenter.show_company_registration_message(
            token=token, company=company
        )
