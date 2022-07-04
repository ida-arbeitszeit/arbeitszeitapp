from tests.data_generators import CooperationGenerator
from tests.flask_integration.flask import ViewTestCase


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.url = "/company/create_cooperation"
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_get_200(
        self,
    ) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_returns_302_when_posting_data(self) -> None:
        response = self.client.post(
            self.url, data={"name": "New Cooperation", "definition": "Coop definition"}
        )
        self.assertEqual(response.status_code, 302)

    def test_returns_400_when_posting_already_existing_coop_name(self) -> None:
        exiting_coop = self.cooperation_generator.create_cooperation()
        response = self.client.post(
            self.url,
            data={
                "name": exiting_coop.name.title(),
                "definition": "Coop definition",
            },
        )
        self.assertEqual(response.status_code, 400)
