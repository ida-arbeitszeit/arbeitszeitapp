from arbeitszeit import email_notifications
from arbeitszeit.use_cases import change_user_password
from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit.use_cases.register_member import RegisterMemberUseCase

from .base_test_case import BaseTestCase


class ChangeUserPasswordTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.reset_password_use_case = self.injector.get(
            change_user_password.ChangeUserPasswordUseCase
        )
        self.register_member_use_case = self.injector.get(RegisterMemberUseCase)
        self.register_company_use_case = self.injector.get(RegisterCompany)

    def _delivered_reset_password_confirmation_message(
        self, sent_to_email: str
    ) -> list[email_notifications.ResetPasswordConfirmation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.ResetPasswordConfirmation)
            and m.email_address == sent_to_email
        ]

    def _create_member(self, email: str) -> None:
        name = "test user name"
        response = self.register_member_use_case.register_member(
            request=RegisterMemberUseCase.Request(
                email=email,
                name=name,
                password="old_password",
            )
        )
        assert not response.is_rejected

    def _create_company(self, email: str) -> None:
        name = "test company name"
        response = self.register_company_use_case.register_company(
            request=RegisterCompany.Request(
                email=email, name=name, password="old_password"
            )
        )
        assert not response.is_rejected

    def test_given_member_reset_password_confirmation_message_is_sent(self):
        sent_to_email = "test@email.com"
        self._create_member(sent_to_email)

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        self.assertTrue(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 1
        )

    def test_given_company_reset_password_confirmation_message_is_sent(self):
        sent_to_email = "test@email.com"
        self._create_company(sent_to_email)

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        self.assertTrue(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 1
        )

    def test_no_message_is_sent_when_email_does_not_exist(self):
        sent_to_email = "test@email.com"
        self._create_member(sent_to_email)

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address="different_email@email.com", new_password="new_password"
            )
        )

        self.assertFalse(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 0
        )
