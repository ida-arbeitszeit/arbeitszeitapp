from typing import Optional, Tuple
from unittest import TestCase

from flask import Flask, _app_ctx_stack

from arbeitszeit.entities import Company, Member
from tests.data_generators import CompanyGenerator, EmailGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class ViewTestCase(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.app = self.injector.get(Flask)
        self.client = self.app.test_client()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.email_generator = self.injector.get(EmailGenerator)

    def tearDown(self) -> None:
        _app_ctx_stack.pop()

    def login_member(
        self,
        member: Optional[Member] = None,
        password: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[Member, str]:
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
        return member, password

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
