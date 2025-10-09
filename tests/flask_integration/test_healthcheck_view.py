from tests.flask_integration.flask import ViewTestCase


class HealthcheckViewTests(ViewTestCase):
    def test_healthcheck_returns_200_ok(self) -> None:
        URL = "/health"
        response = self.client.get(URL)
        assert response.status_code == 200
