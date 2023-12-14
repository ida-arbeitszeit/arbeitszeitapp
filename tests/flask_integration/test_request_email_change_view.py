from parameterized import parameterized

from .flask import LogInUser, ViewTestCase

URL = "/user/request-email-change"
AUTHENTICATED_USER_LOGINS = [
    (LogInUser.member,),
    (LogInUser.unconfirmed_member,),
    (LogInUser.company,),
    (LogInUser.unconfirmed_company,),
    (LogInUser.accountant,),
]


class RequestEmailChangeViewTests(ViewTestCase):
    @parameterized.expand(AUTHENTICATED_USER_LOGINS)
    def test_that_authenticated_users_get_400_response_on_post_without_data(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="POST",
            expected_code=400,
            login=login,
        )

    def test_that_member_gets_redirected_when_posting_with_new_email_address(
        self,
    ) -> None:
        self.login_member()
        response = self.client.post(
            URL,
            data={
                "new_email": "new_email@test.test",
            },
        )
        assert response.status_code == 302

    def test_that_unauthenticated_users_get_redirect_response_on_post_without_data(
        self,
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="POST",
            expected_code=403,
            login=None,
        )

    @parameterized.expand(AUTHENTICATED_USER_LOGINS)
    def test_that_authenticated_users_get_a_200_response_with_get_request(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="GET",
            expected_code=200,
            login=login,
        )

    def test_that_unauthenticated_user_gets_redirect_with_get_requests(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="GET",
            expected_code=302,
            login=None,
        )
