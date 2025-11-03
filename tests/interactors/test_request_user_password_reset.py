from datetime import timedelta

from arbeitszeit import email_notifications
from arbeitszeit.interactors import request_user_password_reset
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class RequestUserPasswordResetTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            request_user_password_reset.RequestUserPasswordResetInteractor
        )

    def _delivered_reset_password_request_message(
        self, sent_to_email: str
    ) -> list[email_notifications.ResetPasswordRequest]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.ResetPasswordRequest)
            and m.email_address == sent_to_email
        ]

    def test_reset_password_request_message_is_sent(self):
        sent_to_email = "test@email.com"
        self.interactor.reset_user_password(
            request_user_password_reset.Request(
                email_address=sent_to_email, reset_token="some_reset_token"
            )
        )

        self.assertEqual(
            len(self._delivered_reset_password_request_message(sent_to_email)), 1
        )

    def test_reset_password_request_messages_are_sent_up_to_threshold_in_a_short_time_span(
        self,
    ):
        sent_to_email = "test@email.com"
        self.datetime_service.freeze_time(datetime_utc(2024, 2, 21, hour=10))
        for _ in range(request_user_password_reset.Config.max_reset_requests + 1):
            self.interactor.reset_user_password(
                request_user_password_reset.Request(
                    email_address=sent_to_email, reset_token="some_reset_token"
                )
            )
            self.datetime_service.advance_time(timedelta(seconds=10))

        self.assertEqual(
            len(self._delivered_reset_password_request_message(sent_to_email)),
            request_user_password_reset.Config.max_reset_requests,
        )

    def test_all_reset_password_request_messages_are_sent_over_a_long_time_period(self):
        sent_to_email = "test@email.com"
        self.datetime_service.freeze_time(datetime_utc(2024, 2, 21, hour=10))
        total_number_sent_over_threshold = (
            request_user_password_reset.Config.max_reset_requests + 5
        )
        for _ in range(total_number_sent_over_threshold):
            self.interactor.reset_user_password(
                request_user_password_reset.Request(
                    email_address=sent_to_email, reset_token="some_reset_token"
                )
            )
            self.datetime_service.advance_time(
                timedelta(minutes=request_user_password_reset.Config.time_threshold_min)
            )

        self.assertEqual(
            len(self._delivered_reset_password_request_message(sent_to_email)),
            total_number_sent_over_threshold,
        )

    def test_reset_password_request_messages_for_different_emails_are_sent(self):
        sent_to_email1 = "test1@email.com"
        sent_to_email2 = "test2@email.com"
        number_of_requests = 3
        self.datetime_service.freeze_time(datetime_utc(2024, 2, 21, hour=10))
        for _ in range(number_of_requests):
            self.interactor.reset_user_password(
                request_user_password_reset.Request(
                    email_address=sent_to_email1, reset_token="some_reset_token"
                )
            )
            self.interactor.reset_user_password(
                request_user_password_reset.Request(
                    email_address=sent_to_email2, reset_token="some_reset_token"
                )
            )
            self.datetime_service.advance_time(timedelta(seconds=10))

        self.assertEqual(
            len(self._delivered_reset_password_request_message(sent_to_email1)),
            number_of_requests,
        )
        self.assertEqual(
            len(self._delivered_reset_password_request_message(sent_to_email2)),
            number_of_requests,
        )
