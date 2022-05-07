from unittest import TestCase

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(RegisterAccountantUseCase)
        self.send_registration_token_use_case = self.injector.get(
            SendAccountantRegistrationTokenUseCase
        )
        self.invitation_presenter = self.injector.get(
            AccountantInvitationPresenterTestImpl
        )

    def test_that_user_with_random_token_and_email_cannot_register(self) -> None:
        request = self.create_request(token="random token")
        response = self.use_case.register_accountant(request)
        self.assertFalse(response.is_accepted)

    def test_that_user_that_was_invited_can_register(self) -> None:
        expected_email = "testmail@test.test"
        token = self.invite_user(email=expected_email)
        request = self.create_request(
            token=token,
            email=expected_email,
        )
        response = self.use_case.register_accountant(request)
        self.assertTrue(response.is_accepted)

    def test_that_token_cannot_be_used_for_registering_email_that_was_was_not_invited(
        self,
    ) -> None:
        token = self.invite_user(email="invited@email.test")
        request = self.create_request(token=token, email="other@email.test")
        response = self.use_case.register_accountant(request)
        self.assertFalse(response.is_accepted)

    def invite_user(self, email: str) -> str:
        self.send_registration_token_use_case.send_accountant_registration_token(
            request=self.send_registration_token_use_case.Request(email=email)
        )
        return self.invitation_presenter.invitations[-1].token

    def create_request(
        self, token: str, email: str = "test@mail.test", name: str = "test name"
    ) -> RegisterAccountantUseCase.Request:
        return self.use_case.Request(
            token=token,
            email=email,
            name=name,
        )
