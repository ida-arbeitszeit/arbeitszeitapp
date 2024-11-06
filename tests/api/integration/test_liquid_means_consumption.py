from tests.api.integration.base_test_case import ApiTestCase


class AnonymousUserTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/consumptions/liquid_means_of_production"

    def test_get_request_of_anonymous_user_returns_method_not_allowed_error(
        self,
    ) -> None:
        response = self.client.get(self.url)
        assert response.status_code == 405

    def test_post_request_of_anonymous_user_returns_unauthorized_error(self) -> None:
        response = self.client.post(self.url)
        assert response.status_code == 401


class AuthenticatedCompanyTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/consumptions/liquid_means_of_production"
        self.login_company()

    def test_post_request_of_authenticated_company_returns_ok_with_valid_input(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        response = self.client.post(self.url, json={"plan_id": plan, "amount": 10})
        assert response.status_code == 200

    def test_post_request_of_authenticated_company_returns_bad_request_with_invalid_input(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        response = self.client.post(self.url, json={"plan_id": plan})
        assert response.status_code == 400


class AuthenticatedMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/consumptions/liquid_means_of_production"
        self.login_member()

    def test_post_request_of_authenticated_member_returns_unauthorized(
        self,
    ) -> None:
        response = self.client.post(self.url)
        assert response.status_code == 401
