from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.token import FlaskTokenService

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.send_token_use_case = self.injector.get(
            SendAccountantRegistrationTokenUseCase
        )
        self.token_service = self.injector.get(FlaskTokenService)

    def test_get_proper_200_response_with_valid_token(self) -> None:
        token = self.token_service.generate_token("test@test.test")
        response = self.client.get(f"/accountant/signup/{token}")
        self.assertEqual(response.status_code, 200)
