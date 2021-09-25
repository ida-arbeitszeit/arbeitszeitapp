from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.member_password = "password123"
        self.current_member = self.member_generator.create_member(
            email="member@cp.org",
            password=self.member_password,
        )
        self.url = "/member/suchen"
        self.company_url = "/company/suchen"
        self.default_data = dict(
            select="Name",
            search="",
        )
        self.login()

    def test_authenticated_users_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_can_posting_empty_search_string_is_valid(self):
        self.default_data["search"] = ""
        response = self.client.post(self.url, data=self.default_data)
        self.assertEqual(response.status_code, 200)

    def test_posting_query_without_query_string_is_invalid(self):
        self.default_data.pop("search")
        response = self.client.post(self.url, data=self.default_data)
        self.assertEqual(response.status_code, 400)

    def test_get_redirected_when_trying_to_access_search_for_company(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, 302)

    def login(self):
        response = self.client.post(
            "/member/login",
            data=dict(
                email=self.current_member.email,
                password=self.member_password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        company_generator = self.injector.get(CompanyGenerator)
        self.company_password = "password123"
        self.current_company = company_generator.create_company(
            password=self.company_password
        )
        self.member_url = "/member/suchen"
        self.url = "/company/suchen"

    def test_company_gets_redirected_when_trying_to_access_member_view(self):
        self.login()
        response = self.client.get(self.member_url)
        self.assertEqual(response.status_code, 302)

    def test_company_can_access_page_when_with_200(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def login(self):
        response = self.client.post(
            "/company/login",
            data=dict(
                email=self.current_company.email,
                password=self.company_password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400


class UnauthenticatedUserTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/suchen"

    def test_unauthenticated_users_get_302(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
