from tests.flask_integration.flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cooperation = self.cooperation_generator.create_cooperation()
        self.login_company()

    def test_that_requesting_view_results_in_200_status_code(self) -> None:
        response = self.client.get(
            f"/user/cooperation_summary/{self.cooperation}/coordinators"
        )
        self.assertEqual(response.status_code, 200)


class MemberViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cooperation = self.cooperation_generator.create_cooperation()
        self.login_member()

    def test_that_requesting_view_results_in_200_status_code(self) -> None:
        response = self.client.get(
            f"/user/cooperation_summary/{self.cooperation}/coordinators"
        )
        self.assertEqual(response.status_code, 200)


class AccountantViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cooperation = self.cooperation_generator.create_cooperation()
        self.login_accountant()

    def test_that_requesting_view_results_in_200_status_code(self) -> None:
        response = self.client.get(
            f"/user/cooperation_summary/{self.cooperation}/coordinators"
        )
        self.assertEqual(response.status_code, 200)
