from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class AnonymousUserTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"

    def test_anonymous_user_gets_redirected_to_start_with_next_url_set_correctly(
        self,
    ):
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/")


class MemberTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"
        self.member = self.login_member()

    def test_member_gets_redirected_to_start_page_with_next_url_set_correctly(
        self,
    ) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/")


class UnconfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company(confirm_company=False)
        self.url = "/company/dashboard"

    def test_unconfirmed_company_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_page_for_unconfirmed_companies(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/company/unconfirmed")
