from typing import Any, Optional

from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/query_companies"

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

    @parameterized.expand(
        [
            (LogInUser.company, 200, dict(select="Email", search="Test search")),
            (LogInUser.member, 302, dict(select="Email", search="Test search")),
        ]
    )
    def test_correct_status_codes_on_post_requests(
        self, login: LogInUser, expected_code: int, data: dict[Any, Any]
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="post",
            login=login,
            expected_code=expected_code,
            data=data,
        )


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_that_logged_in_company_gets_200(self) -> None:
        response = self.client.get("/company/query_companies")
        self.assertEqual(response.status_code, 200)

    def test_there_is_no_pagination_button_when_one_company_exists(self) -> None:
        self.company_generator.create_company()
        response = self.client.get("/company/query_companies")
        self.assertNotIn(r'class="pagination-link', response.text)

    def test_there_is_a_pagination_button_when_16_companies_exist(self) -> None:
        for _ in range(16):
            self.company_generator.create_company()
        response = self.client.get("/company/query_companies")
        self.assertIn(r'class="pagination-link', response.text)
