from tests.api.integration.base_test_case import ApiTestCase


class UnauthentificatedUserTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"

    def test_unauthenticated_user_cannot_get_plans_and_gets_401(self):
        expected_message = "You have to authenticate before using this service."
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], expected_message)


class AuthentificatedCompanyTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"
        self.login_company()

    def test_authenticated_company_can_get_plan_and_gets_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 200)


class AuthentificatedMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"
        self.login_member()

    def test_authenticated_member_can_get_plans_and_gets_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 200)

    def test_get_returns_200_with_correct_offset_param(self):
        response = self.client.get(self.url + "?offset=1")
        self.assertEqual(response.status_code, 200)

    def test_get_returns_200_with_correct_offset_and_limit_params(self):
        response = self.client.get(self.url + "?offset=1&limit=1")
        self.assertEqual(response.status_code, 200)

    def test_get_returns_400_when_letters_are_in_offset_param(
        self,
    ):
        response = self.client.get(self.url + "?offset=abc")
        self.assertEqual(response.status_code, 400)

    def test_post_returns_405(self):
        response = self.client.post(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)
