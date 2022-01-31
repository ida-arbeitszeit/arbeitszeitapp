from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import AccountTypes
from arbeitszeit.repositories import AccountRepository, CompanyRepository
from arbeitszeit.token import ConfirmationEmail, TokenDeliverer, TokenService


@dataclass
class RegisterCompanyResponse:
    class RejectionReason(Exception, Enum):
        company_already_exists = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RegisterCompanyRequest:
    email: str
    name: str
    password: str


@inject
@dataclass
class RegisterCompany:
    company_repository: CompanyRepository
    account_repository: AccountRepository
    datetime_service: DatetimeService
    token_service: TokenService
    token_deliverer: TokenDeliverer

    def __call__(self, request: RegisterCompanyRequest) -> RegisterCompanyResponse:
        try:
            self._register_company(request)
            self._create_confirmation_mail(request)
        except RegisterCompanyResponse.RejectionReason as reason:
            return RegisterCompanyResponse(rejection_reason=reason)
        return RegisterCompanyResponse(rejection_reason=None)

    def _register_company(self, request: RegisterCompanyRequest) -> None:
        if self.company_repository.has_company_with_email(request.email):
            raise RegisterCompanyResponse.RejectionReason.company_already_exists
        means_account = self.account_repository.create_account(AccountTypes.p)
        resources_account = self.account_repository.create_account(AccountTypes.r)
        labour_account = self.account_repository.create_account(AccountTypes.a)
        products_account = self.account_repository.create_account(AccountTypes.prd)
        registered_on = self.datetime_service.now()
        self.company_repository.create_company(
            request.email,
            request.name,
            request.password,
            means_account,
            labour_account,
            resources_account,
            products_account,
            registered_on,
        )

    def _create_confirmation_mail(self, request: RegisterCompanyRequest) -> None:
        token = self.token_service.generate_token(request.email)
        self.token_deliverer.deliver_confirmation_token(
            ConfirmationEmail(token=token, email=request.email)
        )
