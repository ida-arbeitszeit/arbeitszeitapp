from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


def get_url(company: UUID) -> str:
    return f"user/company/{company}/account_r"


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company()
        self.url = get_url(self.company)

    def test_anonymous_user_gets_status_code_302_on_get_request(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=None,
            expected_code=302,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_authenticated_users_get_status_code_200_on_get_requests(
        self, login: LogInUser, expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class ShowTransfersTests(ViewTestCase):
    def test_that_company_shows_debit_transfer_value_with_negative_sign(self) -> None:
        EXPECTED_VALUE = Decimal(116)
        email, password = ("any@company.com", "12345678")
        company = self.company_generator.create_company_record(
            email=email, password=password
        )
        self.login_company(email=email, password=password)
        self.transfer_generator.create_transfer(
            debit_account=company.raw_material_account, value=EXPECTED_VALUE
        )
        response = self.client.get(get_url(company.id))
        assert response.status_code == 200
        assert f"-{EXPECTED_VALUE}" in response.text
