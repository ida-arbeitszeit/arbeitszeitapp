from enum import Enum, auto
from typing import Any, Optional
from uuid import UUID

from flask import Flask, current_app

from arbeitszeit.injector import Injector, Module
from arbeitszeit_db.repositories import DatabaseGatewayImpl
from arbeitszeit_flask.dependency_injection import FlaskModule
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.url_index import GeneralUrlIndex
from tests import data_generators
from tests.db.base_test_case import DatabaseTestCase
from tests.flask_integration.dependency_injection import FlaskTestingModule
from tests.flask_integration.mail_service import MockEmailService
from tests.lazy_property import _lazy_property


class FlaskTestCase(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.dependencies.extend([FlaskModule(), FlaskTestingModule()])
        self.dependencies.extend(self.get_injection_modules())
        self.injector = Injector(self.dependencies)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        if hasattr(self, "app_context"):
            self.app_context.pop()
        super().tearDown()

    def email_service(self) -> MockEmailService:
        return current_app.extensions["arbeitszeit_email_plugin"]

    def get_injection_modules(self) -> list[Module]:
        # tests inheriting from this class can override this method in
        # order to change dependency injection behaviour (useful for the
        # flask configuration)
        return []

    accountant_generator = _lazy_property(data_generators.AccountantGenerator)
    company_generator = _lazy_property(data_generators.CompanyGenerator)
    consumption_generator = _lazy_property(data_generators.ConsumptionGenerator)

    cooperation_generator = _lazy_property(data_generators.CooperationGenerator)
    coordination_transfer_request_generator = _lazy_property(
        data_generators.CoordinationTransferRequestGenerator
    )
    database_gateway = _lazy_property(DatabaseGatewayImpl)
    email_generator = _lazy_property(data_generators.EmailGenerator)
    member_generator = _lazy_property(data_generators.MemberGenerator)
    plan_generator = _lazy_property(data_generators.PlanGenerator)
    registered_hours_worked_generator = _lazy_property(
        data_generators.RegisteredHoursWorkedGenerator
    )
    token_service = _lazy_property(FlaskTokenService)
    transfer_generator = _lazy_property(data_generators.TransferGenerator)
    url_index = _lazy_property(GeneralUrlIndex)
    worker_affiliation_generator = _lazy_property(
        data_generators.WorkerAffiliationGenerator
    )


class LogInUser(Enum):
    member = auto()
    unconfirmed_member = auto()
    company = auto()
    unconfirmed_company = auto()
    accountant = auto()


class ViewTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()

    def login_member(
        self,
        password: str = "password123",
        email: str | None = None,
        confirm_member: bool = True,
    ) -> UUID:
        if email is None:
            email = self.email_generator.get_random_email()
        member_id = self._get_or_create_member(email, password)
        self._login_member(email, password)
        if confirm_member:
            self._confirm_member(email)
        return member_id

    def _get_or_create_member(self, email: str, password: str) -> UUID:
        if (
            member := self.database_gateway.get_members()
            .with_email_address(email)
            .first()
        ):
            return member.id
        return self.member_generator.create_member(
            email=email, password=password, confirmed=False
        )

    def _login_member(
        self,
        email: str,
        password: str,
    ) -> None:
        response = self.client.post(
            "/login-member",
            data=dict(
                email=email,
                password=password,
            ),
            follow_redirects=True,
        )
        if not response.status_code < 400:
            raise AssertionError(
                f"Failed to log in member. Response status code: {response.status_code}."
            )

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
        if not response.status_code < 400:
            raise AssertionError(
                f"Failed to log in accountant. Response status code: {response.status_code}."
            )
        return accountant

    def login_company(
        self,
        password: str = "password123",
        email: str | None = None,
        confirm_company: bool = True,
    ) -> UUID:
        if email is None:
            email = self.email_generator.get_random_email()
        company_id = self._get_or_create_company(email, password)
        self._login_company(email, password)
        if confirm_company:
            self._confirm_company(email)
        return company_id

    def _get_or_create_company(self, email: str, password: str) -> UUID:
        if (
            company := self.database_gateway.get_companies()
            .with_email_address(email)
            .first()
        ):
            return company.id
        return self.company_generator.create_company(
            email=email, password=password, confirmed=False
        )

    def _login_company(
        self,
        email: str,
        password: str,
    ) -> None:
        response = self.client.post(
            "/company/login",
            data=dict(
                email=email,
                password=password,
            ),
            follow_redirects=True,
        )
        if not response.status_code < 400:
            raise AssertionError(
                f"Failed to log in company. Response status code: {response.status_code}."
            )

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
            return self.login_company()
        elif login == LogInUser.unconfirmed_company:
            return self.login_company(confirm_company=False)
        elif login == LogInUser.accountant:
            return self.login_accountant()
