from enum import Enum, auto

from tests.flask_integration.base_test_case import FlaskTestCase


class LogInUser(Enum):
    member = auto()
    company = auto()


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
            json=dict(
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
            json=dict(
                email=email,
                password=password,
            ),
        )
        assert response.status_code < 400

    def login_user(self, login: LogInUser) -> None:
        match login:
            case LogInUser.member:
                self.login_member()
            case LogInUser.company:
                self.login_company()
            case _:
                raise ValueError("Invalid user type")
