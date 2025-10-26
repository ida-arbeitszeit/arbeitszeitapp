from uuid import uuid4

from tests.flask_integration.base_test_case import ViewTestCase

URL = "/company/accept_cooperation_request"


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()

    def test_that_posting_valid_form_data_yields_a_redirect(self) -> None:
        response = self.client.post(
            URL,
            data={
                "plan_id": str(uuid4()),
                "cooperation_id": str(uuid4()),
            },
        )
        self.assertEqual(response.status_code, 302)
