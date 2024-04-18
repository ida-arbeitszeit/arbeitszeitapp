from typing import Optional
from uuid import uuid4

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


class QueryPlansTests(ViewTestCase):
    def test_that_one_plan_name_appears_in_html_when_there_are_two_plans_but_only_one_is_searched_for(
        self,
    ) -> None:
        self.login_member()
        EXPECTED_PLAN_NAME = f"One-{uuid4()}"
        UNEXPECTED_PLAN_NAME = f"Two-{uuid4()}"
        self.plan_generator.create_plan(product_name=EXPECTED_PLAN_NAME)
        self.plan_generator.create_plan(product_name=UNEXPECTED_PLAN_NAME)
        response = self.client.get(
            URL, query_string={"select": "Produktname", "search": EXPECTED_PLAN_NAME}
        )
        assert EXPECTED_PLAN_NAME in response.text
        assert UNEXPECTED_PLAN_NAME not in response.text
