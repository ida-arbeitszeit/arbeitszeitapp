from uuid import uuid4

from .flask import ViewTestCase

URL = "/company/select_productive_consumption"


class NonCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_that_anonymous_user_gets_redirected(self) -> None:
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 302)

    def test_that_member_gets_redirected(self) -> None:
        self.login_member()
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 302)

    def test_that_accountant_gets_redirected(self) -> None:
        self.login_accountant()
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 302)


class CompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_that_logged_in_company_gets_200_response(self) -> None:
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 200)

    def test_that_plan_id_from_query_string_appears_in_response_html(self) -> None:
        EXPECTED_PLAN_ID = uuid4()
        response = self.client.get(URL + f"?plan_id={EXPECTED_PLAN_ID}")
        assert str(EXPECTED_PLAN_ID) in response.text
