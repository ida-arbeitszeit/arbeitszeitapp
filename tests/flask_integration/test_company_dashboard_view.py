from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class AnonymousUserTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"

    def test_anonymous_user_gets_redirected_to_start_with_next_url_set_correctly(
        self,
    ):
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/")


class MemberTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"
        self.member = self.login_member()

    def test_member_gets_redirected_to_start_page_with_next_url_set_correctly(
        self,
    ) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/")


class UnconfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company(confirm_company=False)
        self.url = "/company/dashboard"

    def test_unconfirmed_company_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_page_for_unconfirmed_companies(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/company/unconfirmed")


class IconTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/dashboard"
        self.login_company()

    def test_that_icon_for_creating_new_plan_is_shown_on_company_dashboard(
        self,
    ) -> None:
        """
        This test asserts that the expected SVG path of the "create new plan icon",
        as specified in `arbeitszeit_flask/templates/icons/file-circle-plus.html`,
        appears on the company dashboard.
        """

        CREATE_NEW_PLAN_ICON = (
            """<path fill="currentColor" d="M0 64C0 28.65 28.65 0 64 """
            """0H224V128C224 145.7 238.3 160 256 160H384V198.6C310.1 219.5 256 """
            """287.4 256 368C256 427.1 285.1 479.3 329.7 511.3C326.6 511.7 323.3 """
            """512 320 512H64C28.65 512 0 483.3 0 448V64zM256 128V0L384 128H256zM288 """
            """368C288 288.5 352.5 224 432 224C511.5 224 576 288.5 576 368C576 447.5 """
            """511.5 512 432 512C352.5 512 288 447.5 288 368zM448 303.1C448 295.2 """
            """440.8 287.1 432 287.1C423.2 287.1 416 295.2 416 303.1V351.1H368C359.2 """
            """351.1 352 359.2 352 367.1C352 376.8 359.2 383.1 368 383.1H416V431."""
            """1C416 440.8 423.2 447.1 432 447.1C440.8 447.1 448 440.8 448 431.1V383."""
            """1H496C504.8 383.1 512 376.8 512 367.1C512 359.2 504.8 351.1 496 351."""
            """1H448V303.1z"></path>"""
        )
        response = self.client.get(self.url)
        self.assertIn(CREATE_NEW_PLAN_ICON, response.text)
