from tests.flask_integration.flask import ViewTestCase


class AnonymousUserTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/purchases"

    def test_anonymous_user_gets_302(
        self,
    ):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_gets_redirected_to_start_with_next_url_set_correctly(
        self,
    ):
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/?next=%2Fcompany%2Fpurchases")


class MemberTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/purchases"
        self.member = self.login_member(confirm_member=True)

    def test_member_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_member_gets_redirected_to_start_page_with_next_url_set_correctly(
        self,
    ) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.location, "/?next=%2Fcompany%2Fpurchases")


class UnconfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company(confirm_company=False)
        self.url = "/company/purchases"

    def test_unconfirmed_company_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_page_for_unconfirmed_companies(self) -> None:
        response = self.client.get(self.url)
        assert response.location == "/company/unconfirmed"


class ConfirmedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company(confirm_company=True)
        self.url = "/company/purchases"

    def test_company_gets_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
