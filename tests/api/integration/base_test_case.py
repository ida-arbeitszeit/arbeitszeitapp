from tests.flask_integration.flask import FlaskTestCase


class ApiTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_prefix = "/api/v1"
        self.client = self.app.test_client()

    def login_member(self) -> None:
        password = "password123"
        email = self.email_generator.get_random_email()
        self.member_generator.create_member(
            password=password, email=email, confirmed=True
        )
        response = self.client.post(
            self.url_prefix + "/auth/login_member",
            data=dict(
                email=email,
                password=password,
            ),
        )
        assert response.status_code < 400

    def login_company(self) -> None:
        password = "password123"
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(
            password=password, email=email, confirmed=True
        )
        response = self.client.post(
            self.url_prefix + "/auth/login_company",
            data=dict(
                email=email,
                password=password,
            ),
        )
        assert response.status_code < 400
