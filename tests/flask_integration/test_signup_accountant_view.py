from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.send_token_use_case = self.injector.get(
            SendAccountantRegistrationTokenUseCase
        )
        self.accountant_invitation_presenter = self.injector.get(
            AccountantInvitationPresenterTestImpl
        )

    def test_get_proper_200_response_with_valid_token(self) -> None:
        token = self.invite_accountant("test@test.test")
        response = self.client.get(f"/accountant/signup/{token}")
        self.assertEqual(response.status_code, 200)

    def invite_accountant(self, email: str) -> str:
        self.send_token_use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=email,
            )
        )
        return self.accountant_invitation_presenter.invitations[-1].token
