from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class ChangeEmailAddressViewTests(ViewTestCase):
    def test_that_anonymous_users_get_redirected_with_invalid_token(self) -> None:
        self.assert_response_has_expected_code(
            url=self._construct_url(token="invalid-token"),
            method="GET",
            expected_code=302,
            login=None,
        )

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_registered_users_get_404_on_get_request_with_invalid_token(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=self._construct_url("invalid_token"),
            method="GET",
            expected_code=404,
            login=login,
        )

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_registered_users_get_200_on_get_request_with_valid_token(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=self._construct_url(token=self._valid_token()),
            method="GET",
            expected_code=200,
            login=login,
        )

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_registered_users_get_redirected_on_post_request_with_valid_token_to_account_details_url(
        self, login: LogInUser
    ) -> None:
        self.login_user(login)
        response = self.client.post(
            self._construct_url(token=self._valid_token()), follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/user/account")

    def _valid_token(self) -> str:
        return self.token_service.generate_token(
            input="old_email@mail.org:new_email@mail.org"
        )

    def _construct_url(self, token: str) -> str:
        return f"/user/change-email/{token}"
