from .flask import ViewTestCase


class StartViewTests(ViewTestCase):
    def test_that_user_gets_redirected_to_original_target_url_after_successful_login(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "my password"
        expected_target_url = "/member/query_plans"
        self.member_generator.create_member(
            email=expected_email, password=expected_password, confirmed=True
        )
        response = self.client.get(expected_target_url)
        assert response.location == "/"
        response = self.client.post(
            "/member/login",
            data=dict(
                email=expected_email,
                password=expected_password,
            ),
        )
        assert response.location.endswith(expected_target_url)

    def test_member_can_login_after_having_attempted_to_visit_a_company_route_before(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "my password"
        company_route = "/company/dashboard"

        self.member_generator.create_member(
            email=expected_email, password=expected_password, confirmed=True
        )
        self.client.get(company_route)
        self.client.post(
            "/member/login",
            data=dict(
                email=expected_email,
                password=expected_password,
            ),
            follow_redirects=True,
        )
        response2 = self.client.post(
            "/member/login",
            data=dict(
                email=expected_email,
                password=expected_password,
            ),
        )
        assert response2.location.endswith("/member/dashboard")
