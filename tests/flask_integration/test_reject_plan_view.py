from .flask import LogInUser, ViewTestCase


class AccountantTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_that_logged_in_accountant_gets_redirected(self) -> None:
        plan = self.plan_generator.create_plan(approved=False, rejected=True)
        self.assert_response_has_expected_code(
            url=f"/accountant/plans/{plan}/reject",
            method="post",
            login=LogInUser.accountant,
            expected_code=302,
        )

    def test_that_unauthenticated_user_gets_redirected(self) -> None:
        plan = self.plan_generator.create_plan(approved=False, rejected=True)
        self.assert_response_has_expected_code(
            url=f"/accountant/plans/{plan}/reject",
            method="post",
            login=LogInUser.accountant,
            expected_code=302,
        )
