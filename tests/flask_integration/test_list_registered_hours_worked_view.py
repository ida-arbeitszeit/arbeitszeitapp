from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class CompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/list_registered_hours_worked"

    def test_company_can_access_view_with_200(self) -> None:
        self.login_company()
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_worker_id_is_shown_in_html_when_working_hours_have_been_registered(
        self,
    ) -> None:
        EXPECTED_WORKER_ID = self.member_generator.create_member()
        self._register_hours_worked(EXPECTED_WORKER_ID)
        response = self.client.get(self.url, follow_redirects=True)
        assert str(EXPECTED_WORKER_ID) in response.text

    def _register_hours_worked(self, worker_id: UUID) -> None:
        company_email = "mail@mail.org"
        company_password = "password123"
        company = self.company_generator.create_company(
            workers=[worker_id], email=company_email, password=company_password
        )
        self.login_company(email=company_email, password=company_password)
        self.registered_hours_worked_generator.register_hours_worked(
            company=company, worker=worker_id, hours=Decimal("10")
        )


class NonCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/list_registered_hours_worked"

    @parameterized.expand(
        [
            LogInUser.member,
            LogInUser.accountant,
        ]
    )
    def test_logged_in_non_company_users_get_redirected(
        self, log_in_user: LogInUser
    ) -> None:
        self.login_user(log_in_user)
        response = self.client.get(self.url)
        assert response.status_code == 302
