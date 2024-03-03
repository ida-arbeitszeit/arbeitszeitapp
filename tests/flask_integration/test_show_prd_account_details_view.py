from typing import Optional
from uuid import UUID

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class IntegrationTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_logged_in_users_get_200_on_get_requests_if_company_that_owns_account_exists(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        company = self.company_generator.create_company()
        self.assert_response_has_expected_code(
            url=self.create_url(account_owner=company),
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_anonymous_users_get_302_on_get_requests_if_company_that_owns_account_exists(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.assert_response_has_expected_code(
            url=self.create_url(account_owner=company),
            method="get",
            login=None,
            expected_code=302,
        )

    def test_the_user_icon_appears_in_html_if_private_consumption_was_registered(
        self,
    ) -> None:
        self.login_company()
        provider = self.company_generator.create_company()
        self.register_private_consumption(provider=provider)
        response = self.client.get(self.create_url(account_owner=provider))
        assert "fa-user" in response.text

    def test_the_industry_icon_appears_in_html_if_productive_consumption_was_registered(
        self,
    ) -> None:
        self.login_company()
        provider = self.company_generator.create_company()
        self.register_productive_consumption(provider=provider)
        response = self.client.get(self.create_url(account_owner=provider))
        assert "fa-industry" in response.text

    def register_private_consumption(self, provider: UUID) -> None:
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_private_consumption(plan=plan)

    def register_productive_consumption(self, provider: UUID) -> None:
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)

    def create_url(self, account_owner: UUID) -> str:
        return f"user/company/{account_owner}/account_prd"
