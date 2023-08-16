from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.presenters import CompanyRegistrationMessagePresenter
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RegisterCompany:
    datetime_service: DatetimeService
    company_registration_message_presenter: CompanyRegistrationMessagePresenter
    password_hasher: PasswordHasher
    database: DatabaseGateway

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
        company: Optional[records.Company]
        record = (
            self.database.get_account_credentials()
            .with_email_address(request.email)
            .joined_with_email_address_and_company()
            .first()
        )
        if not record:
            means_account = self.database.create_account()
            resources_account = self.database.create_account()
            labour_account = self.database.create_account()
            products_account = self.database.create_account()
            registered_on = self.datetime_service.now()
            self.database.create_email_address(address=request.email, confirmed_on=None)
            credentials = self.database.create_account_credentials(
                email_address=request.email,
                password_hash=self.password_hasher.calculate_password_hash(
                    request.password
                ),
            )
            self._create_confirmation_mail(request.email)
        else:
            credentials, email, company = record
            if company:
                raise self.Response.RejectionReason.company_already_exists
            if not self.password_hasher.is_password_matching_hash(
                password=request.password, password_hash=credentials.password_hash
            ):
                raise self.Response.RejectionReason.user_password_is_invalid
            means_account = self.database.create_account()
            resources_account = self.database.create_account()
            labour_account = self.database.create_account()
            products_account = self.database.create_account()
            registered_on = self.datetime_service.now()
        company = self.database.create_company(
            account_credentials=credentials.id,
            name=request.name,
            means_account=means_account,
            labour_account=labour_account,
            resource_account=resources_account,
            products_account=products_account,
            registered_on=registered_on,
        )
        return company.id

    def _create_confirmation_mail(self, email_address: str) -> None:
        self.company_registration_message_presenter.show_company_registration_message(
            email_address=email_address
        )
