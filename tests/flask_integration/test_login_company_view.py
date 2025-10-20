from .base_test_case import ViewTestCase


class LoginTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/login"

    def test_get_200_when_accessing_login_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_200_when_posting_to_url(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_redirected_when_posting_correct_credentials(self) -> None:
        self.company_generator.create_company(email="a@b.c", password="testpassword")
        response = self.client.post(
            self.url,
            data=dict(
                email="a@b.c",
                password="testpassword",
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_get_401_when_posting_incorrect_credentials(self) -> None:
        self.company_generator.create_company(email="a@b.c", password="testpassword")
        response = self.client.post(
            self.url,
            data=dict(
                email="a@b.c",
                password="wrongpassword",
            ),
        )
        self.assertEqual(response.status_code, 401)


class StartViewTests(ViewTestCase):
    def test_that_user_gets_redirected_to_original_target_url_after_successful_login(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "my password"
        expected_target_url = "/user/query_plans"
        self.company_generator.create_company(
            email=expected_email, password=expected_password, confirmed=True
        )
        response = self.client.get(expected_target_url)
        assert response.location == "/"
        response = self.client.post(
            "/company/login",
            data=dict(
                email=expected_email,
                password=expected_password,
            ),
        )
        assert response.location.endswith(expected_target_url)

    def test_company_can_log_in_after_having_attempted_to_visit_a_member_route_before(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "my password"
        member_route = "/member/dashboard"

        self.company_generator.create_company(
            email=expected_email, password=expected_password, confirmed=True
        )
        self.client.get(member_route)
        self.client.post(
            "/company/login",
            data=dict(
                email=expected_email,
                password=expected_password,
            ),
            follow_redirects=True,
        )
        response2 = self.client.post(
            "/company/login",
            data=dict(
                email=expected_email,
                password=expected_password,
            ),
        )
        assert response2.location.endswith("/company/dashboard")
