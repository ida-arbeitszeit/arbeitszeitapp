from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/create_cooperation"

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


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/create_cooperation"

    def test_returns_302_when_posting_data(self) -> None:
        self.assert_response_has_expected_code(
            method="post",
            url=self.url,
            login=LogInUser.company,
            expected_code=302,
            data={"name": "New Cooperation", "definition": "Coop definition"},
        )

    def test_returns_400_when_posting_already_existing_coop_name(self) -> None:
        name_of_existing_coop = "Existing Cooperation"
        self.cooperation_generator.create_cooperation(name=name_of_existing_coop)
        self.assert_response_has_expected_code(
            method="post",
            url=self.url,
            login=LogInUser.company,
            expected_code=400,
            data={
                "name": name_of_existing_coop,
                "definition": "Coop definition",
            },
        )
