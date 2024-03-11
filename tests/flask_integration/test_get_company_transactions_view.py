from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company()
        self.url = f"user/company/{self.company}/transactions"

    def test_anonymous_user_gets_status_code_302_on_get_request(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=None,
            expected_code=302,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_authenticated_users_get_status_code_200_on_get_requests(
        self, login: LogInUser, expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )
