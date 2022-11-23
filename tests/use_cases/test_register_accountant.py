from unittest import TestCase

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.data_generators import AccountantGenerator, CompanyGenerator, MemberGenerator

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
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.accountant_generator = self.injector.get(AccountantGenerator)

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

    def test_that_user_can_register_with_email_already_belonging_to_a_member(
        self,
    ) -> None:
        email_address = "test@test.test"
        token = self.invite_user(email=email_address)
        self.member_generator.create_member_entity(email=email_address)
        request = self.create_request(token=token, email=email_address)
        response = self.use_case.register_accountant(request)
        self.assertTrue(response.is_accepted)

    def test_that_user_can_register_with_email_already_belonging_to_a_company(
        self,
    ) -> None:
        email_address = "test@test.test"
        token = self.invite_user(email=email_address)
        self.company_generator.create_company_entity(email=email_address)
        request = self.create_request(token=token, email=email_address)
        response = self.use_case.register_accountant(request)
        self.assertTrue(response.is_accepted)

    def test_that_user_cannot_register_twice_with_same_email_address(self) -> None:
        expected_email = "testmail@test.test"
        token = self.invite_user(email=expected_email)
        request = self.create_request(
            token=token,
            email=expected_email,
        )
        self.use_case.register_accountant(request)
        response = self.use_case.register_accountant(request)
        self.assertFalse(response.is_accepted)

    def test_that_no_user_id_is_returned_when_trying_to_create_accountant_with_email_address_of_another_accountant(
        self,
    ) -> None:
        email_address = "test@test.test"
        token = self.invite_user(email=email_address)
        self.accountant_generator.create_accountant(email_address=email_address)
        request = self.create_request(token=token, email=email_address)
        response = self.use_case.register_accountant(request)
        self.assertIsNone(response.user_id)

    def test_that_original_email_address_is_returned_when_registering_successful(
        self,
    ) -> None:
        for email_address in self.example_email_addresses:
            with self.subTest():
                token = self.invite_user(email=email_address)
                request = self.create_request(token=token, email=email_address)
                response = self.use_case.register_accountant(request)
                self.assertEqual(response.email_address, email_address)

    def test_that_original_email_address_is_returned_when_failing_to_register(
        self,
    ) -> None:
        for email_address in self.example_email_addresses:
            with self.subTest():
                token = self.invite_user(email=email_address)
                request = self.create_request(token=token, email=email_address)
                self.accountant_generator.create_accountant(email_address=email_address)
                response = self.use_case.register_accountant(request)
                self.assertEqual(response.email_address, email_address)

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
            password="test password",
        )

    example_email_addresses = [
        "test@test.test",
        "test2@test.test",
    ]
