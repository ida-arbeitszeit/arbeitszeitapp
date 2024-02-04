from typing import Optional
from uuid import UUID

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/my_accounts/account_prd"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_logged_in_users_get_200_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_anonymous_users_get_302_on_get_requests(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url, method="get", login=None, expected_code=302
        )

    def test_after_one_private_consumption_the_user_icon_appears_in_html(self) -> None:
        company = self.login_company().id
        self._make_sale_to_member(provider=company)
        response = self.client.get(self.url)
        assert "fa-user" in response.text

    def test_after_one_productive_consumption_the_industry_icon_appears_in_html(
        self,
    ) -> None:
        company = self.login_company().id
        self._make_sale_to_company(provider=company)
        response = self.client.get(self.url)
        assert "fa-industry" in response.text

    def _make_sale_to_member(self, provider: UUID) -> None:
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_private_consumption(plan=plan.id)

    def _make_sale_to_company(self, provider: UUID) -> None:
        plan = self.plan_generator.create_plan(planner=provider)
        self.consumption_generator.create_fixed_means_consumption(plan=plan.id)
