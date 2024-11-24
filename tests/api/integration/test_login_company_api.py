from tests.api.integration.base_test_case import ApiTestCase


class ListLoginCompanyTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/auth/login_company"

    def test_get_returns_405(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_returns_200_with_correct_data_in_form(self) -> None:
        email = "some@mail.org"
        password = "safe123"
        self.company_generator.create_company(email=email, password=password)
        response = self.client.post(self.url, json=dict(email=email, password=password))
        self.assertEqual(response.status_code, 200)

    def test_post_returns_415_with_correct_data_in_query_string_but_missing_data_in_form(
        self,
    ) -> None:
        email = "some@mail.org"
        password = "safe123"
        self.company_generator.create_company(email=email, password=password)
        response = self.client.post(
            self.url, query_string=dict(email=email, password=password)
        )
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.content_type, "application/json")

    def test_post_returns_401_with_incorrect_data(self) -> None:
        email = "some@mail.org"
        password = "safe123"
        self.company_generator.create_company(email=email, password=password)
        response = self.client.post(
            self.url, json=dict(email=email + ".com", password=password)
        )
        self.assertEqual(response.status_code, 401)
