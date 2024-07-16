from enum import Enum, auto
from typing import Any, List, Optional
from unittest import TestCase
from uuid import UUID

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.injector import Module
from arbeitszeit.records import Company
from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from arbeitszeit_flask.token import FlaskTokenService
from tests.data_generators import (
    AccountantGenerator,
    CompanyGenerator,
    ConsumptionGenerator,
    CooperationGenerator,
    CoordinationTransferRequestGenerator,
    EmailGenerator,
    MemberGenerator,
    PlanGenerator,
)
from tests.flask_integration.mail_service import MockEmailService
from tests.markers import database_required

from .dependency_injection import get_dependency_injector


class LogInUser(Enum):
    member = auto()
    unconfirmed_member = auto()
    company = auto()
    unconfirmed_company = auto()
    accountant = auto()


@database_required
class FlaskTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector(self.get_injection_modules())
        self.db = self.injector.get(SQLAlchemy)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db.session.flush()
        self.db.drop_all()
        self.db.create_all()
        self.db.session.flush()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)

    def tearDown(self) -> None:
        self.db.session.flush()
        self.app_context.pop()
        super().tearDown()

    def get_injection_modules(self) -> List[Module]:
        return []

    def email_service(self) -> MockEmailService:
        return current_app.extensions["arbeitszeit_email_plugin"]


class ViewTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.email_generator = self.injector.get(EmailGenerator)
        self.accountant_generator = self.injector.get(AccountantGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.coordination_transfer_request_generator = self.injector.get(
            CoordinationTransferRequestGenerator
        )
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
        self.token_service = self.injector.get(FlaskTokenService)

    def login_member(
        self,
        member: Optional[UUID] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
        confirm_member: bool = True,
    ) -> UUID:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if member is None:
            member = self.member_generator.create_member(
                password=password, email=email, confirmed=False
            )
        response = self.client.post(
            "/login-member",
            data=dict(
                email=email,
                password=password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400
        if confirm_member:
            self._confirm_member(email)
        return member

    def _confirm_member(
        self,
        email: str,
    ) -> None:
        token = FlaskTokenService().generate_token(email)
        response = self.client.get(
            f"/confirm-member/{token}",
            follow_redirects=True,
        )
        assert response.status_code < 400

    def login_accountant(self) -> UUID:
        email = self.email_generator.get_random_email()
        password = "password123"
        accountant = self.accountant_generator.create_accountant(
            email_address=email, password=password
        )
        response = self.client.post(
            "/accountant/login",
            data=dict(
                password=password,
                email=email,
            ),
        )
        self.assertLess(response.status_code, 400)
        return accountant

    def login_company(
        self,
        company: Optional[UUID] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
        confirm_company: bool = True,
    ) -> Company:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if company is None:
            company = self.company_generator.create_company(
                password=password, email=email, confirmed=False
            )
        response = self.client.post(
            "/company/login",
            data=dict(
                email=email,
                password=password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400
        if confirm_company:
            self._confirm_company(email)
        updated_company = (
            self.database_gateway.get_companies().with_email_address(email).first()
        )
        assert updated_company
        return updated_company

    def _confirm_company(
        self,
        email: str,
    ) -> None:
        token = FlaskTokenService().generate_token(email)
        response = self.client.get(
            f"/company/confirm/{token}",
            follow_redirects=True,
        )
        assert response.status_code < 400

    def assert_response_has_expected_code(
        self,
        url: str,
        method: str,
        expected_code: int,
        login: Optional[LogInUser],
        data: Optional[dict[Any, Any]] = None,
    ) -> None:
        if login:
            self.login_user(login)
        if method.lower() == "get":
            response = self.client.get(url, query_string=data)
        elif method.lower() == "post":
            response = self.client.post(url, data=data)
        else:
            raise ValueError(f"Unknown {method=}")

        assert (
            response.status_code == expected_code
        ), f"Expected status code {expected_code} but got {response.status_code}"

    def login_user(self, login: LogInUser) -> UUID:
        if login == LogInUser.member:
            return self.login_member()
        elif login == LogInUser.unconfirmed_member:
            return self.login_member(confirm_member=False)
        elif login == LogInUser.company:
            return self.login_company().id
        elif login == LogInUser.unconfirmed_company:
            return self.login_company(confirm_company=False).id
        elif login == LogInUser.accountant:
            return self.login_accountant()
