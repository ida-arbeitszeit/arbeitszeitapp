from enum import Enum, auto
from typing import Any, Generic, List, Optional, Type, TypeVar
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
    CoordinationTenureGenerator,
    CoordinationTransferRequestGenerator,
    EmailGenerator,
    MemberGenerator,
    PlanGenerator,
    TransactionGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.flask_integration.mail_service import MockEmailService
from tests.markers import database_required

from .dependency_injection import get_dependency_injector

T = TypeVar("T")


# This class is a descriptor.
class _lazy_property(Generic[T]):
    def __init__(self, cls: Type[T]):
        """Implement a lazy property for the FlaskTestCase.  If the
        implementor asks for this attribute then it is generated on
        demand and cached.
        """
        self.cls = cls

    def __set_name__(self, owner, name: str) -> None:
        self._attribute_name = name

    def __get__(self, obj: Any, objtype=None) -> T:
        cache = obj._lazy_property_cache
        instance = cache.get(self._attribute_name)
        if instance is None:
            instance = obj.injector.get(self.cls)
            cache[self._attribute_name] = instance
        return instance

    def __set__(self, obj: Any, value: T) -> None:
        raise Exception("This attribute is read-only")


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
        self._lazy_property_cache: dict[str, Any] = dict()
        self.injector = get_dependency_injector(self.get_injection_modules())
        self.db = self.injector.get(SQLAlchemy)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db.session.flush()
        self.db.drop_all()
        self.db.create_all()
        self.db.session.flush()

    def tearDown(self) -> None:
        self._lazy_property_cache = dict()
        self.db.session.flush()
        self.app_context.pop()
        super().tearDown()

    def get_injection_modules(self) -> List[Module]:
        return []

    def email_service(self) -> MockEmailService:
        return current_app.extensions["arbeitszeit_email_plugin"]

    # It would be nice to have the following list sorted
    # alphabetically
    accountant_generator = _lazy_property(AccountantGenerator)
    company_generator = _lazy_property(CompanyGenerator)
    consumption_generator = _lazy_property(ConsumptionGenerator)
    cooperation_generator = _lazy_property(CooperationGenerator)
    coordination_tenure_generator = _lazy_property(CoordinationTenureGenerator)
    coordination_transfer_request_generator = _lazy_property(
        CoordinationTransferRequestGenerator
    )
    database_gateway = _lazy_property(DatabaseGatewayImpl)
    datetime_service = _lazy_property(FakeDatetimeService)
    email_generator = _lazy_property(EmailGenerator)
    member_generator = _lazy_property(MemberGenerator)
    plan_generator = _lazy_property(PlanGenerator)
    token_service = _lazy_property(FlaskTokenService)
    transaction_generator = _lazy_property(TransactionGenerator)


class ViewTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()

    def login_member(
        self,
        password: Optional[str] = None,
        email: Optional[str] = None,
        confirm_member: bool = True,
    ) -> UUID:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if not self.database_gateway.get_members().with_email_address(email).first():
            self.member_generator.create_member(
                email=email, password=password, confirmed=False
            )
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
        if confirm_member:
            self._confirm_member(email)
        member = self.database_gateway.get_members().with_email_address(email).first()
        assert member
        return member.id

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
        password: Optional[str] = None,
        email: Optional[str] = None,
        confirm_company: bool = True,
    ) -> Company:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if not self.database_gateway.get_companies().with_email_address(email).first():
            self.company_generator.create_company(
                email=email, password=password, confirmed=False
            )
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
        if confirm_company:
            self._confirm_company(email)
        company = (
            self.database_gateway.get_companies().with_email_address(email).first()
        )
        assert company
        return company

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
