from arbeitszeit.interactors.confirm_company import ConfirmCompanyInteractor
from arbeitszeit.interactors.register_accountant import RegisterAccountantInteractor
from arbeitszeit.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(RegisterAccountantInteractor)
        self.send_registration_token_interactor = self.injector.get(
            SendAccountantRegistrationTokenInteractor
        )
        self.confirm_company_interactor = self.injector.get(ConfirmCompanyInteractor)

    def test_that_user_that_was_invited_can_register(self) -> None:
        expected_email = "testmail@test.test"
        self.invite_user(email=expected_email)
        request = self.create_request(
            email=expected_email,
        )
        response = self.interactor.register_accountant(request)
        self.assertTrue(response.is_accepted)

    def test_that_user_can_register_with_email_already_belonging_to_a_member(
        self,
    ) -> None:
        email_address = "test@test.test"
        self.invite_user(email=email_address)
        self.member_generator.create_member(email=email_address)
        request = self.create_request(email=email_address)
        response = self.interactor.register_accountant(request)
        self.assertTrue(response.is_accepted)

    def test_that_user_can_register_with_email_already_belonging_to_a_company(
        self,
    ) -> None:
        email_address = "test@test.test"
        self.invite_user(email=email_address)
        self.company_generator.create_company(email=email_address)
        request = self.create_request(email=email_address)
        response = self.interactor.register_accountant(request)
        self.assertTrue(response.is_accepted)

    def test_that_user_registering_an_accountant_confirms_the_email_address_also_for_companies_with_the_same_address(
        self,
    ) -> None:
        email_address = "test@test.test"
        self.company_generator.create_company(email=email_address, confirmed=False)
        self.invite_user(email=email_address)
        request = self.create_request(email=email_address)
        self.interactor.register_accountant(request)
        response = self.confirm_company_interactor.confirm_company(
            ConfirmCompanyInteractor.Request(
                email_address=email_address,
            )
        )
        assert not response.is_confirmed

    def test_that_user_cannot_register_twice_with_same_email_address(self) -> None:
        expected_email = "testmail@test.test"
        self.invite_user(email=expected_email)
        request = self.create_request(
            email=expected_email,
        )
        self.interactor.register_accountant(request)
        response = self.interactor.register_accountant(request)
        self.assertFalse(response.is_accepted)

    def test_that_no_user_id_is_returned_when_trying_to_create_accountant_with_email_address_of_another_accountant(
        self,
    ) -> None:
        email_address = "test@test.test"
        self.invite_user(email=email_address)
        self.accountant_generator.create_accountant(email_address=email_address)
        request = self.create_request(email=email_address)
        response = self.interactor.register_accountant(request)
        self.assertIsNone(response.user_id)

    def test_that_original_email_address_is_returned_when_registering_successful(
        self,
    ) -> None:
        for email_address in self.example_email_addresses:
            with self.subTest():
                self.invite_user(email=email_address)
                request = self.create_request(email=email_address)
                response = self.interactor.register_accountant(request)
                self.assertEqual(response.email_address, email_address)

    def test_that_original_email_address_is_returned_when_failing_to_register(
        self,
    ) -> None:
        for email_address in self.example_email_addresses:
            with self.subTest():
                request = self.create_request(email=email_address)
                self.accountant_generator.create_accountant(email_address=email_address)
                response = self.interactor.register_accountant(request)
                self.assertEqual(response.email_address, email_address)

    def invite_user(self, email: str) -> None:
        self.send_registration_token_interactor.send_accountant_registration_token(
            request=self.send_registration_token_interactor.Request(email=email)
        )

    def create_request(
        self, email: str = "test@mail.test", name: str = "test name"
    ) -> RegisterAccountantInteractor.Request:
        return self.interactor.Request(
            email=email,
            name=name,
            password="test password",
        )

    example_email_addresses = [
        "test@test.test",
        "test2@test.test",
    ]
