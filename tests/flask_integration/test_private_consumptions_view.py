from typing import Optional

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/consumptions"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 302),
            (LogInUser.member, 200),
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

    def test_logged_in_member_gets_200_after_consuming_something(self) -> None:
        member = self.login_member()
        self.consumption_generator.create_private_consumption(consumer=member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class AnonymousUserTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/consumptions"

    def test_anonymous_user_gets_redirected_to_start_page(
        self,
    ):
        response = self.client.get(self.url, follow_redirects=True)
        assert response.request.url == self.url_index.get_start_page_url()


class CompanyTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/consumptions"
        self.login_company()

    def test_company_gets_redirected_to_start_page(
        self,
    ) -> None:
        response = self.client.get(self.url, follow_redirects=True)
        assert response.request.url == self.url_index.get_start_page_url()

    def test_user_type_in_session_is_set_to_none_when_company_accesses_page(
        self,
    ) -> None:
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "company")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])


class UnconfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member(confirm_member=False)
        self.url = "/member/consumptions"

    def test_unconfirmed_member_gets_302(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_page_for_unconfirmed_members(self) -> None:
        response = self.client.get(self.url, follow_redirects=True)
        assert response.request.url == self.url_index.get_unconfirmed_member_url()
