from arbeitszeit import email_notifications
from arbeitszeit.use_cases import change_user_password
from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase
from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase

from .base_test_case import BaseTestCase


class ChangeUserPasswordTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.reset_password_use_case = self.injector.get(
            change_user_password.ChangeUserPasswordUseCase
        )
        self.login_member_use_case = self.injector.get(LogInMemberUseCase)
        self.login_company_use_case = self.injector.get(LogInCompanyUseCase)
        self.login_accountant_use_case = self.injector.get(LogInAccountantUseCase)

    def _delivered_reset_password_confirmation_message(
        self, sent_to_email: str
    ) -> list[email_notifications.ResetPasswordConfirmation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.ResetPasswordConfirmation)
            and m.email_address == sent_to_email
        ]

    def test_given_member_reset_password_confirmation_message_is_sent(self):
        sent_to_email = "test@email.com"
        self.member_generator.create_member(
            email=sent_to_email, password="old_password"
        )

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
        self.company_generator.create_company(
            email=sent_to_email, password="old_password"
        )

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        self.assertTrue(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 1
        )

    def test_given_accountant_reset_password_confirmation_message_is_sent(self):
        sent_to_email = "test@email.com"
        self.accountant_generator.create_accountant(
            email_address=sent_to_email, password="old_password"
        )

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        self.assertTrue(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 1
        )

    def test_given_member_password_reset_then_user_can_login_with_new_password(self):
        sent_to_email = "test@email.com"
        new_password = "new_password"
        self.member_generator.create_member(
            email=sent_to_email, password="old_password"
        )
        self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password=new_password
            )
        )

        response = self.login_member_use_case.log_in_member(
            LogInMemberUseCase.Request(email=sent_to_email, password=new_password)
        )

        self.assertTrue(response.is_logged_in)

    def test_given_member_password_reset_then_user_cannot_login_with_old_password(self):
        sent_to_email = "test@email.com"
        old_password = "old_password"
        self.member_generator.create_member(email=sent_to_email, password=old_password)
        self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        response = self.login_member_use_case.log_in_member(
            LogInMemberUseCase.Request(email=sent_to_email, password=old_password)
        )

        self.assertFalse(response.is_logged_in)

    def test_given_company_password_reset_then_user_can_login_with_new_password(self):
        sent_to_email = "test@email.com"
        new_password = "new_password"
        self.company_generator.create_company(
            email=sent_to_email, password="old_password"
        )
        self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password=new_password
            )
        )

        response = self.login_company_use_case.log_in_company(
            LogInCompanyUseCase.Request(
                email_address=sent_to_email, password=new_password
            )
        )

        self.assertTrue(response.is_logged_in)

    def test_given_company_password_reset_then_user_cannot_login_with_old_password(
        self,
    ):
        sent_to_email = "test@email.com"
        old_password = "old_password"
        self.company_generator.create_company(
            email=sent_to_email, password=old_password
        )
        self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        response = self.login_company_use_case.log_in_company(
            LogInCompanyUseCase.Request(
                email_address=sent_to_email, password=old_password
            )
        )

        self.assertFalse(response.is_logged_in)

    def test_given_accountant_password_reset_then_user_can_login_with_new_password(
        self,
    ):
        sent_to_email = "test@email.com"
        new_password = "new_password"
        self.accountant_generator.create_accountant(
            email_address=sent_to_email, password="old_password"
        )
        self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password=new_password
            )
        )

        response = self.login_accountant_use_case.log_in_accountant(
            LogInAccountantUseCase.Request(
                email_address=sent_to_email, password=new_password
            )
        )

        self.assertIsNotNone(response.user_id)

    def test_given_accountant_password_reset_then_user_cannot_login_with_old_password(
        self,
    ):
        sent_to_email = "test@email.com"
        old_password = "old_password"
        self.accountant_generator.create_accountant(
            email_address=sent_to_email, password=old_password
        )
        self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address=sent_to_email, new_password="new_password"
            )
        )

        response = self.login_accountant_use_case.log_in_accountant(
            LogInAccountantUseCase.Request(
                email_address=sent_to_email, password=old_password
            )
        )

        self.assertIsNone(response.user_id)

    def test_given_member_no_password_is_updated_when_account_with_email_does_not_exist(
        self,
    ):
        sent_to_email = "test@email.com"
        self.member_generator.create_member(
            email=sent_to_email, password="old_password"
        )

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address="non_existent_email@email.com",
                new_password="new_password",
            )
        )

        self.assertFalse(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 0
        )

    def test_given_company_no_password_is_updated_when_account_with_email_does_not_exist(
        self,
    ):
        sent_to_email = "test@email.com"
        self.company_generator.create_company(
            email=sent_to_email, password="old_password"
        )

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address="non_existent_email@email.com",
                new_password="new_password",
            )
        )

        self.assertFalse(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 0
        )

    def test_given_accountant_no_password_is_updated_when_account_with_email_does_not_exist(
        self,
    ):
        sent_to_email = "test@email.com"
        self.accountant_generator.create_accountant(
            email_address=sent_to_email, password="old_password"
        )

        response = self.reset_password_use_case.change_user_password(
            change_user_password.Request(
                email_address="non_existent_email@email.com",
                new_password="new_password",
            )
        )

        self.assertFalse(response.is_changed)
        self.assertEqual(
            len(self._delivered_reset_password_confirmation_message(sent_to_email)), 0
        )
