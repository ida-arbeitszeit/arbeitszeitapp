from tests.data_generators import PlanGenerator

from .flask import LogInUser, ViewTestCase


class AccountantTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_logged_in_accountant_gets_redirected(self) -> None:
        plan = self.plan_generator.create_plan()
        self.assert_response_has_expected_code(
            url=f"/accountant/plans/{plan}/approve",
            method="post",
            login=LogInUser.accountant,
            expected_code=302,
        )

    def test_that_unauthenticated_user_gets_redirected(self) -> None:
        plan = self.plan_generator.create_plan()
        self.assert_response_has_expected_code(
            url=f"/accountant/plans/{plan}/approve",
            method="post",
            login=None,
            expected_code=302,
        )
