from tests.api.integration.base_test_case import ApiTestCase


class ListLoginMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/auth/login_member"

    def test_get_returns_405(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_returns_200_with_correct_data_in_form(self) -> None:
        email = "some@mail.org"
        password = "safe123"
        self.member_generator.create_member(email=email, password=password)
        response = self.client.post(self.url, data=dict(email=email, password=password))
        self.assertEqual(response.status_code, 200)

    def test_post_returns_400_with_correct_data_in_query_string_but_missing_data_in_form(
        self,
    ) -> None:
        email = "some@mail.org"
        password = "safe123"
        self.member_generator.create_member(email=email, password=password)
        response = self.client.post(
            self.url, query_string=dict(email=email, password=password)
        )
        self.assertEqual(response.status_code, 400)

    def test_post_returns_401_with_incorrect_data(self) -> None:
        email = "some@mail.org"
        password = "safe123"
        self.member_generator.create_member(email=email, password=password)
        response = self.client.post(
            self.url, data=dict(email=email + ".com", password=password)
        )
        self.assertEqual(response.status_code, 401)
