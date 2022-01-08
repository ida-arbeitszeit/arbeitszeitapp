from typing import List, Optional, Tuple
from unittest import TestCase

from flask import Flask, _app_ctx_stack
from injector import Module

from arbeitszeit.entities import Company, Member
from project.token import FlaskTokenService
from tests.data_generators import (
    CompanyGenerator,
    EmailGenerator,
    MemberGenerator,
    PlanGenerator,
)

from .dependency_injection import get_dependency_injector


class FlaskTestCase(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector(self.get_injection_modules())
        self.app = self.injector.get(Flask)

    def tearDown(self) -> None:
        _app_ctx_stack.pop()

    def get_injection_modules(self) -> List[Module]:
        return []


class ViewTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.email_generator = self.injector.get(EmailGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)

    def login_member(
        self,
        member: Optional[Member] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[Member, str, str]:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if member is None:
            member = self.member_generator.create_member(password=password, email=email)
        response = self.client.post(
            "/member/login",
            data=dict(
                email=email,
                password=password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400
        return member, password, email

    def confirm_member(
        self,
        member: Optional[Member] = None,
        email: Optional[str] = None,
    ) -> Member:
        if email is None:
            email = self.email_generator.get_random_email()
        if member is None:
            member = self.member_generator.create_member(email=email)
        token = FlaskTokenService().generate_token(email)
        response = self.client.get(
            f"/member/confirm/{token}",
            follow_redirects=True,
        )
        assert response.status_code < 400
        return member

    def login_company(
        self,
        company: Optional[Company] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[Company, str]:
        if password is None:
            password = "password123"
        if email is None:
            email = self.email_generator.get_random_email()
        if company is None:
            company = self.company_generator.create_company(
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
        return company, password
