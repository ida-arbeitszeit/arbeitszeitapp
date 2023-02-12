from tests.data_generators import PlanGenerator
from tests.flask_integration.flask import FlaskTestCase


class ApiTestCase(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_prefix = "/api/v1"
        self.client = self.app.test_client()
        self.plan_generator = self.injector.get(PlanGenerator)
