from tests.api.integration.base_test_case import ApiTestCase


class TestApiDocumentation(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/doc/"

    def test_docs_return_code_200(self) -> None:
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_swagger_json_file_can_get_accessed(self) -> None:
        swagger_json_url = self.url_prefix + "/swagger.json"
        response = self.client.get(swagger_json_url)
        assert response.status_code < 400

    def test_swagger_css_file_can_get_accessed(self) -> None:
        response = self.client.get("/swaggerui/swagger-ui.css")
        assert response.status_code < 400

    def test_swagger_javascript_file_can_get_accessed(self) -> None:
        response = self.client.get("/swaggerui/swagger-ui-bundle.js")
        assert response.status_code < 400
