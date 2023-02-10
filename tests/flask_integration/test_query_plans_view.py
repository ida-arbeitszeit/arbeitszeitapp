from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/query_plans"
        self.company_url = "/company/query_plans"
        self.default_data = dict(select="Produktname", search="", radio="activation")
        self.member = self.login_member()

    def test_authenticated_users_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_getting_empty_search_string_is_valid(self):
        self.default_data["search"] = ""
        response = self.client.get(self.url, data=self.default_data)
        self.assertEqual(response.status_code, 200)

    def test_getting_query_with_invalid_sorting_category_results_in_400(self):
        self.default_data["radio"] = "invalid category"
        response = self.client.get(self.url, data=self.default_data)
        self.assertEqual(response.status_code, 400)

    def test_get_redirected_when_trying_to_access_query_plans_for_company(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, 302)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_url = "/member/query_plans"
        self.url = "/company/query_plans"
        self.company = self.login_company()

    def test_company_gets_redirected_when_trying_to_access_member_view(self):
        response = self.client.get(self.member_url)
        self.assertEqual(response.status_code, 302)

    def test_company_can_access_page_when_with_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class UnauthenticatedUserTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/query_plans"

    def test_unauthenticated_users_get_302(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
