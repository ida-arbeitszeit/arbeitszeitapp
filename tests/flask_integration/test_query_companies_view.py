from typing import Any, Dict

from parameterized import parameterized

from .flask import LogInUser, ViewTestCase

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
