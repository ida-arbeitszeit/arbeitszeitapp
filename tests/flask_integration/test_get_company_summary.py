from uuid import uuid4

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()

    def test_get_404_when_company_does_not_exist(self) -> None:
        url = f"/member/company_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_company_exists(self) -> None:
        company = self.company_generator.create_company()
        url = f"/member/company_summary/{company}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_get_404_when_company_does_not_exist(self) -> None:
        url = f"/company/company_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_company_exists(self) -> None:
        company = self.company_generator.create_company()
        url = f"/company/company_summary/{company}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedAccountantTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = self.login_accountant()

    def test_get_404_when_company_does_not_exist(self) -> None:
        url = f"/accountant/company_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_company_exists(self) -> None:
        company = self.company_generator.create_company()
        url = f"/accountant/company_summary/{company}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
