from tests.flask_integration.flask import ViewTestCase


class FaviconTests(ViewTestCase):
    def test_that_getting_favicon_route_yields_200(self) -> None:
        response = self.client.get("/static/favicon.ico")
        assert response.status_code == 200

    def test_that_a_favicon_is_linked_in_base_template(self) -> None:
        response = self.client.get("/")
        assert (
            """<link rel="shortcut icon" href="/static/favicon.ico">""" in response.text
        )
