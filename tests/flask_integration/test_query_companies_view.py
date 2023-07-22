from typing import Any, Dict, Optional

from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
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
            url="/company/query_companies",
            method="get",
            login=login,
            expected_code=expected_code,
        )

    @parameterized.expand(
        [
            ("/member/query_companies", LogInUser.member, 200),
            ("/member/query_companies", LogInUser.company, 302),
            ("/member/query_companies", LogInUser.accountant, 302),
            ("/company/query_companies", LogInUser.company, 200),
            ("/company/query_companies", LogInUser.member, 302),
            ("/company/query_companies", LogInUser.accountant, 302),
        ]
    )
    def test_that_authentication_rejects_requests_by_wrong_account_types(
        self, url: str, login: LogInUser, expected_status: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=login,
            expected_code=expected_status,
        )

    @parameterized.expand(
        [
            (LogInUser.company, 200, dict(select="Email", search="Test search")),
            (LogInUser.company, 400, dict(select="ABC", search="Test search")),
            (LogInUser.company, 200, None),
        ]
    )
    def test_correct_handling_of_form_data_for_company_view(
        self, login: LogInUser, expected_code: int, data: Optional[Dict[str, Any]]
    ) -> None:
        self.assert_response_has_expected_code(
            url="/company/query_companies",
            method="get",
            login=login,
            expected_code=expected_code,
            data=data,
        )

    @parameterized.expand(
        [
            (LogInUser.member, 200, dict(select="Email", search="Test search")),
            (LogInUser.member, 400, dict(select="ABC", search="Test search")),
            (LogInUser.member, 200, None),
        ]
    )
    def test_correct_handling_of_form_data_for_member_view(
        self, login: LogInUser, expected_code: int, data: Optional[Dict[str, Any]]
    ) -> None:
        self.assert_response_has_expected_code(
            url="/member/query_companies",
            method="get",
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
