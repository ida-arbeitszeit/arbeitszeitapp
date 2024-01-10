from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class ChangeEmailAddressViewTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_the_route_returns_not_implemented_status(
        self, login: LogInUser
    ) -> None:
        # This test must be removed as soon as the proper functionality to
        # change ones emails address is implemented.
        self.assert_response_has_expected_code(
            url=self._construct_url("abc"),
            method="GET",
            expected_code=501,
            login=login,
        )

    def test_that_anonymous_users_get_redirected(self) -> None:
        self.assert_response_has_expected_code(
            url=self._construct_url("abc"),
            method="GET",
            expected_code=302,
            login=None,
        )

    def _construct_url(self, token: str) -> str:
        return f"/user/change-email/{token}"
