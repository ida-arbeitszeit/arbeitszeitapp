from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser

from .flask import ViewTestCase

URL = "/user/query_plans"


class UserAccessTests(ViewTestCase):
    @parameterized.expand(
        [
            (LogInUser.accountant,),
            (LogInUser.company,),
            (LogInUser.member,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_authenticated_users_receive_200_on_get_request(
        self, login: Optional[LogInUser]
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=200,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant,),
            (LogInUser.company,),
            (LogInUser.member,),
            (LogInUser.unconfirmed_member,),
            (LogInUser.unconfirmed_company,),
        ]
    )
    def test_that_authenticated_users_receive_200_when_there_is_an_active_plan(
        self, login: Optional[LogInUser]
    ) -> None:
        self.plan_generator.create_plan()
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=login,
            expected_code=200,
        )

    def test_that_anonymous_users_get_redirected_on_get_request(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="get",
            login=None,
            expected_code=302,
        )
