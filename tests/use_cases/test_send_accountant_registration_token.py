from unittest import TestCase

from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.data_generators import AccountantGenerator, CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(SendAccountantRegistrationTokenUseCase)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.accountant_generator = self.injector.get(AccountantGenerator)
        self.invitation_presenter = self.injector.get(
            AccountantInvitationPresenterTestImpl
        )

    def test_can_send_registration_token_to_email_that_is_already_registered_as_member(
        self,
    ) -> None:
        member_email = "test@test.test"
        self.member_generator.create_member_entity(email=member_email)
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=member_email,
            )
        )
        self.assertTrue(self.invitation_presenter.invitations)

    def test_can_send_registration_token_to_email_that_is_already_registered_as_company(
        self,
    ) -> None:
        company_email = "test@test.test"
        self.company_generator.create_company_entity(email=company_email)
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=company_email,
            )
        )
        self.assertTrue(self.invitation_presenter.invitations)

    def test_cannot_send_registration_token_to_email_that_is_already_registered_as_accountant(
        self,
    ) -> None:
        accountant_email = "test@test.test"
        self.accountant_generator.create_accountant(email_address=accountant_email)
        pre_use_case_invitation_count = len(self.invitation_presenter.invitations)
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=accountant_email,
            )
        )
        self.assertEqual(
            len(self.invitation_presenter.invitations), pre_use_case_invitation_count
        )

    def test_that_invitation_is_presented_for_correct_email_address(self) -> None:
        expected_email = "test@mail.test"
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=expected_email,
            )
        )
        self.assertEqual(
            self.invitation_presenter.invitations[-1].email, expected_email
        )
