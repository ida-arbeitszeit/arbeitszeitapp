from typing import Optional

from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class UserAccountDetailsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/user/account"

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
        ]
    )
    def test_that_authenticated_users_can_access_the_view(
        self, user_type: Optional[LogInUser]
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="GET",
            expected_code=200,
            login=user_type,
        )

    def test_that_unauthenticated_user_is_redirected(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="GET",
            expected_code=302,
            login=None,
        )

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
        ]
    )
    def test_that_response_contains_user_id(self, login: LogInUser) -> None:
        member = self.login_user(login)
        response = self.client.get(self.url)
        assert str(member) in response.text
