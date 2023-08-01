from .flask import ViewTestCase


class StartViewTests(ViewTestCase):
    def test_that_user_gets_redirected_to_original_target_url_after_successful_login(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "my password"
        expected_target_url = "/company/query_plans"
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

    def test_company_can_login_after_having_attempted_to_visit_a_member_route_before(
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
