from typing import Any, Dict
from uuid import uuid4

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase

URL = "/user/query_companies"


class QueryCompanyViewTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.accountant,),
            (LogInUser.company,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_authenticated_users_get_200_when_requesting_with_get(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=200,
        )

    def test_that_anonymous_users_get_redirected_when_requesting_with_get(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=None,
            expected_code=302,
        )

    @parameterized.expand(
        [
            (LogInUser.member, dict(select="Email", search="Test search")),
            (LogInUser.member, dict(select="Name", search="Test search")),
        ]
    )
    def test_that_200_is_returned_when_sending_valid_form_data(
        self, login: LogInUser, data: Dict[str, Any]
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=200,
            data=data,
        )

    @parameterized.expand(
        [
            (LogInUser.member, dict(select="ABC", search="Test search")),
            (LogInUser.member, dict(select="123", search="Test search")),
        ]
    )
    def test_that_400_is_returned_when_sending_invalid_form_data(
        self, login: LogInUser, data: Dict[str, Any]
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=400,
            data=data,
        )

    def test_that_one_company_name_appears_in_html_when_there_are_two_companies_but_only_one_is_searched_for(
        self,
    ) -> None:
        self.login_member()
        EXPECTED_COMPANY_NAME = f"One-{uuid4()}"
        UNEXPECTED_COMPANY_NAME = f"Two-{uuid4()}"
        self.company_generator.create_company(name=EXPECTED_COMPANY_NAME)
        self.company_generator.create_company(name=UNEXPECTED_COMPANY_NAME)
        response = self.client.get(
            URL, query_string={"select": "Name", "search": EXPECTED_COMPANY_NAME}
        )
        assert EXPECTED_COMPANY_NAME in response.text
        assert UNEXPECTED_COMPANY_NAME not in response.text
