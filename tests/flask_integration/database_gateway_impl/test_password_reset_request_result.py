from datetime import datetime, timedelta
from uuid import uuid4

from arbeitszeit import records
from tests.data_generators import EmailGenerator
from tests.datetime_service import FakeDatetimeService

from ..flask import FlaskTestCase


class PasswordResetRequestResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.email_generator = self.injector.get(EmailGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def _generateResetToken(self) -> str:
        return str(uuid4())

    def _create_password_reset_request(self, email_address: str) -> None:
        self.database_gateway.create_password_reset_request(
            email_address=email_address,
            reset_token=self._generateResetToken(),
            created_at=self.datetime_service.now(),
        )

    def _generate_email_address(self) -> str:
        email_address = self.email_generator.get_random_email()
        self.database_gateway.create_email_address(
            address=email_address,
            confirmed_on=self.datetime_service.now_minus_ten_days(),
        )
        return email_address

    def _check_all_results_for_same_email(
        self,
        result_records: list[records.PasswordResetRequest],
        expected_email_address: str,
    ) -> bool:
        return all(
            result_record.email_address == expected_email_address
            for result_record in result_records
        )

    def test_querying_password_reset_request_by_email(self) -> None:
        email_address = self._generate_email_address()
        other_email_address = self._generate_email_address()
        self.datetime_service.freeze_time(datetime(2021, 2, 13, hour=10))

        self._create_password_reset_request(email_address)
        self._create_password_reset_request(other_email_address)

        result_records = list(
            self.database_gateway.get_password_reset_requests().with_email_address(
                email_address
            )
        )
        assert len(result_records) == 1
        assert self._check_all_results_for_same_email(result_records, email_address)

    def test_multiple_password_reset_requests_can_exist_for_given_email(self) -> None:
        email_address = self._generate_email_address()
        self.datetime_service.freeze_time(datetime(2021, 2, 13, hour=10))

        self._create_password_reset_request(email_address)
        self._create_password_reset_request(email_address)
        self._create_password_reset_request(email_address)

        result_records = list(
            self.database_gateway.get_password_reset_requests().with_email_address(
                email_address
            )
        )
        assert len(result_records) == 3
        assert self._check_all_results_for_same_email(result_records, email_address)

    def test_querying_password_reset_requests_after_datetime_threshold(self) -> None:
        email_address = self._generate_email_address()
        self.datetime_service.freeze_time(datetime(2021, 2, 13, hour=10))

        self._create_password_reset_request(email_address)
        self.datetime_service.advance_time(timedelta(hours=1))
        self._create_password_reset_request(email_address)
        self.datetime_service.advance_time(timedelta(minutes=1))
        self._create_password_reset_request(email_address)
        self.datetime_service.advance_time(timedelta(minutes=1))
        self._create_password_reset_request(email_address)

        result_records = list(
            self.database_gateway.get_password_reset_requests()
            .with_email_address(email_address)
            .with_creation_date_after(
                self.datetime_service.now() - timedelta(minutes=30)
            )
        )

        assert len(result_records) == 3
        assert self._check_all_results_for_same_email(result_records, email_address)

    def test_querying_interleaved_non_spammed_and_spammed_requests(self) -> None:
        spammed_email_address = self._generate_email_address()
        not_spammed_email_address = self._generate_email_address()
        self.datetime_service.freeze_time(datetime(2021, 2, 13, hour=10))

        self._create_password_reset_request(not_spammed_email_address)
        self.datetime_service.advance_time(timedelta(hours=2))
        self._create_password_reset_request(not_spammed_email_address)
        self.datetime_service.advance_time(timedelta(hours=2))
        self._create_password_reset_request(spammed_email_address)
        self.datetime_service.advance_time(timedelta(seconds=10))
        self._create_password_reset_request(spammed_email_address)
        self.datetime_service.advance_time(timedelta(seconds=10))
        self._create_password_reset_request(spammed_email_address)
        self.datetime_service.advance_time(timedelta(seconds=10))
        self._create_password_reset_request(spammed_email_address)
        self._create_password_reset_request(not_spammed_email_address)
        self.datetime_service.advance_time(timedelta(minutes=10))
        self._create_password_reset_request(not_spammed_email_address)

        spammed_result_records = list(
            self.database_gateway.get_password_reset_requests()
            .with_email_address(spammed_email_address)
            .with_creation_date_after(
                self.datetime_service.now() - timedelta(minutes=30)
            )
        )
        not_spammed_result_records = list(
            self.database_gateway.get_password_reset_requests()
            .with_email_address(not_spammed_email_address)
            .with_creation_date_after(
                self.datetime_service.now() - timedelta(minutes=30)
            )
        )

        assert len(spammed_result_records) == 4
        assert self._check_all_results_for_same_email(
            spammed_result_records, spammed_email_address
        )
        assert len(not_spammed_result_records) == 2
        assert self._check_all_results_for_same_email(
            not_spammed_result_records, not_spammed_email_address
        )
