from typing import List, Optional
from unittest import TestCase
from uuid import UUID

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from arbeitszeit.entities import Company, Member
from arbeitszeit.injector import Module
from arbeitszeit_flask.database.repositories import CompanyRepository, MemberRepository
from arbeitszeit_flask.token import FlaskTokenService
from tests.data_generators import (
    AccountantGenerator,
    CompanyGenerator,
    EmailGenerator,
    MemberGenerator,
)
from tests.markers import database_required

from .dependency_injection import get_dependency_injector


@database_required
class FlaskTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector(self.get_injection_modules())
        self.db = self.injector.get(SQLAlchemy)
        self.app = self.injector.get(Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db.drop_all()
        self.db.create_all()

    def tearDown(self) -> None:
        self.app_context.pop()
        super().tearDown()

    def get_injection_modules(self) -> List[Module]:
        return []


class ViewTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.email_generator = self.injector.get(EmailGenerator)
        self.member_repository = self.injector.get(MemberRepository)
        self.company_repository = self.injector.get(CompanyRepository)
        self.accountant_generator = self.injector.get(AccountantGenerator)

    def login_member(
        self,
        member: Optional[Member] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
        confirm_member: bool = True,
    ) -> Member:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if member is None:
            member = self.member_generator.create_member_entity(
                password=password, email=email, confirmed=False
            )
        response = self.client.post(
            "/member/login",
            data=dict(
                email=email,
                password=password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400
        if confirm_member:
            self._confirm_member(email)
        updated_member = (
            self.member_repository.get_members().with_email_address(email).first()
        )
        assert updated_member
        return updated_member

    def _confirm_member(
        self,
        email: str,
    ) -> None:
        token = FlaskTokenService().generate_token(email)
        response = self.client.get(
            f"/member/confirm/{token}",
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
        company: Optional[Company] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
        confirm_company: bool = True,
    ) -> Company:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if company is None:
            company = self.company_generator.create_company_entity(
                password=password, email=email
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
            self.company_repository.get_companies().with_email_address(email).first()
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
