from uuid import uuid4

from .flask import ViewTestCase

URL = "/company/register_productive_consumption"


class NonCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_that_anonymous_user_gets_redirected(self) -> None:
        response = self.client.post(URL)
        self.assertEqual(response.status_code, 302)

    def test_that_member_gets_redirected(self) -> None:
        self.login_member()
        response = self.client.post(URL)
        self.assertEqual(response.status_code, 302)

    def test_that_accountant_gets_redirected(self) -> None:
        self.login_accountant()
        response = self.client.post(URL)
        self.assertEqual(response.status_code, 302)


class CompanyPostTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_that_logged_in_company_receives_400_when_posting_non_existing_plan_id(
        self,
    ) -> None:
        response = self.client.post(
            URL,
            data=dict(plan_id=str(uuid4()), amount=3, type_of_consumption="fixed"),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_receives_400_when_posting_invalid_type_of_consumption(
        self,
    ) -> None:
        response = self.client.post(
            URL,
            data=dict(
                plan_id=self.create_plan(), amount=3, type_of_consumption="unknown"
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_receives_400_when_posting_incomplete_data(
        self,
    ) -> None:
        response = self.client.post(
            URL,
            data=dict(plan_id=self.create_plan(), amount=3),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_gets_redirected_when_posting_valid_data(
        self,
    ) -> None:
        response = self.client.post(
            URL,
            data=dict(
                plan_id=self.create_plan(), amount=3, type_of_consumption="fixed"
            ),
        )
        self.assertEqual(response.status_code, 302)

    def create_plan(self) -> str:
        return str(self.plan_generator.create_plan())
