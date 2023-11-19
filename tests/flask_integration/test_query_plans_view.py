from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser

from .flask import ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 302),
            (LogInUser.member, 200),
        ]
    )
    def test_get_correct_response_from_member_page(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url="/member/query_plans",
            method="get",
            login=login,
            expected_code=expected_code,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_get_correct_response_from_company_page(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url="/company/query_plans",
            method="get",
            login=login,
            expected_code=expected_code,
        )


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/query_plans"
        self.company_url = "/company/query_plans"
        self.default_data = dict(select="Produktname", search="", radio="activation")
        self.member = self.login_member()

    def test_getting_empty_search_string_is_valid(self):
        self.default_data["search"] = ""
        response = self.client.get(self.url, data=self.default_data)
        self.assertEqual(response.status_code, 200)

    def test_getting_query_with_invalid_sorting_category_results_in_400(self):
        self.default_data["radio"] = "invalid category"
        response = self.client.get(self.url, data=self.default_data)
        self.assertEqual(response.status_code, 400)
