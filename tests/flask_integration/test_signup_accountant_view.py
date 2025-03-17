from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.send_token_use_case = self.injector.get(
            SendAccountantRegistrationTokenUseCase
        )

    def test_get_proper_200_response_with_valid_token(self) -> None:
        token = self.token_service.generate_token("test@test.test")
        response = self.client.get(f"/accountant/signup/{token}")
        self.assertEqual(response.status_code, 200)

    def test_post_proper_400_response_with_invalid_token(self) -> None:
        token = "test token"
        response = self.client.post(f"/accountant/signup/{token}")
        assert response.status_code == 400
