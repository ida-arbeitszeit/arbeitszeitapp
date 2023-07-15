from tests.api.integration.base_test_case import ApiTestCase


class UnauthenticatedUsersTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_unauthenticated_user_gets_401_with_valid_path_params(self):
        valid_plan_id = str(self.plan_generator.create_plan().id)
        valid_url = self.create_url(valid_plan_id)
        response = self.client.get(valid_url)
        self.assertEqual(response.status_code, 401)

    def create_url(self, path_param: str) -> str:
        url = self.url_prefix + "/plans/" + path_param
        return url


class AuthenticatedCompanyTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()

    def test_get_returns_200_with_valid_path_parameter(self) -> None:
        valid_plan_id = str(self.plan_generator.create_plan().id)
        valid_url = self.create_url(path_param=valid_plan_id)
        response = self.client.get(valid_url)
        self.assertEqual(response.status_code, 200)

    def create_url(self, path_param: str) -> str:
        url = self.url_prefix + "/plans/" + path_param
        return url


class AuthenticatedMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_member()

    def test_get_returns_200_with_valid_path_parameter(self) -> None:
        valid_plan_id = str(self.plan_generator.create_plan().id)
        valid_url = self.create_url(path_param=valid_plan_id)
        response = self.client.get(valid_url)
        self.assertEqual(response.status_code, 200)

    def test_get_returns_404_without_path_parameter(self) -> None:
        invalid_url = self.create_url(path_param="")
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def create_url(self, path_param: str) -> str:
        url = self.url_prefix + "/plans/" + path_param
        return url
