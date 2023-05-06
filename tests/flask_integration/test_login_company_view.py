from .flask import ViewTestCase


class StartViewTests(ViewTestCase):
    def test_that_user_gets_redirected_after_successful_login_to_original_target_url(
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
