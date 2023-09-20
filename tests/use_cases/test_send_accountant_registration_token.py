from arbeitszeit import email_notifications
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(SendAccountantRegistrationTokenUseCase)

    def test_can_send_registration_token_to_email_that_is_already_registered_as_member(
        self,
    ) -> None:
        member_email = "test@test.test"
        self.member_generator.create_member(email=member_email)
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=member_email,
            )
        )
        self.delivered_notifications()

    def test_can_send_registration_token_to_email_that_is_already_registered_as_company(
        self,
    ) -> None:
        company_email = "test@test.test"
        self.company_generator.create_company_record(email=company_email)
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=company_email,
            )
        )
        assert self.delivered_notifications()

    def test_cannot_send_registration_token_to_email_that_is_already_registered_as_accountant(
        self,
    ) -> None:
        accountant_email = "test@test.test"
        self.accountant_generator.create_accountant(email_address=accountant_email)
        pre_use_case_invitation_count = len(self.delivered_notifications())
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=accountant_email,
            )
        )
        assert len(self.delivered_notifications()) == pre_use_case_invitation_count

    def test_that_invitation_is_presented_for_correct_email_address(self) -> None:
        expected_email = "test@mail.test"
        self.use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(
                email=expected_email,
            )
        )
        self.assertEqual(
            self.latest_delivered_notification().email_address, expected_email
        )

    def latest_delivered_notification(self) -> email_notifications.AccountantInvitation:
        notifications = self.delivered_notifications()
        assert notifications
        return notifications[-1]

    def delivered_notifications(self) -> list[email_notifications.AccountantInvitation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.AccountantInvitation)
        ]
