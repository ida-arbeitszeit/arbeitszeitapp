from datetime import UTC, datetime, timedelta
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors import (
    confirm_company,
    confirm_member,
    get_user_account_details,
)
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class GetUserAccountDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            get_user_account_details.GetUserAccountDetailsInteractor
        )
        self.confirm_member_interactor = self.injector.get(
            confirm_member.ConfirmMemberInteractor
        )
        self.confirm_company_interactor = self.injector.get(
            confirm_company.ConfirmCompanyInteractor
        )

    def test_that_no_user_info_is_returned_if_requested_user_id_is_not_registered(
        self,
    ) -> None:
        request = get_user_account_details.Request(user_id=uuid4())
        response = self.interactor.get_user_account_details(request)
        assert response.user_info is None

    def test_that_returned_user_id_is_equal_to_member_id_requested(self) -> None:
        member = self.member_generator.create_member()
        request = get_user_account_details.Request(user_id=member)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.id == member

    def test_that_returned_user_id_is_equal_to_company_id_requested(self) -> None:
        company = self.company_generator.create_company()
        request = get_user_account_details.Request(user_id=company)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.id == company

    def test_that_returned_user_id_is_equal_to_accountant_id_requested(self) -> None:
        accountant = self.accountant_generator.create_accountant()
        request = get_user_account_details.Request(user_id=accountant)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.id == accountant

    def test_that_users_email_address_is_shown(self) -> None:
        for expected_email_address in [
            "testmail@test.test",
            "other@test.mail",
        ]:
            member = self.member_generator.create_member(email=expected_email_address)
            request = get_user_account_details.Request(user_id=member)
            response = self.interactor.get_user_account_details(request)
            assert response.user_info
            assert response.user_info.email_address == expected_email_address

    def test_that_unconfirmed_member_has_no_email_confirmation_timestamp(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        request = get_user_account_details.Request(user_id=member)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert not response.user_info.email_address_confirmation_timestamp

    def test_that_confirmed_member_has_email_confirmation_timestamp(self) -> None:
        member = self.member_generator.create_member(confirmed=True)
        request = get_user_account_details.Request(user_id=member)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.email_address_confirmation_timestamp

    @parameterized.expand(
        [
            datetime_utc(2000, 1, 1),
            datetime_utc(2000, 1, 2),
        ]
    )
    def test_that_confirmation_timestamp_for_member_is_the_time_when_their_account_was_confirmed(
        self, expected_timestamp: datetime
    ) -> None:
        member_email = "test@test.test"
        self.datetime_service.freeze_time(expected_timestamp - timedelta(days=1))
        member = self.member_generator.create_member(
            confirmed=False, email=member_email
        )
        self.datetime_service.freeze_time(expected_timestamp)
        self._confirm_member(member_email)
        self.datetime_service.advance_time(timedelta(days=1))
        request = get_user_account_details.Request(user_id=member)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert (
            response.user_info.email_address_confirmation_timestamp
            == expected_timestamp
        )

    @parameterized.expand(
        [
            datetime_utc(2000, 1, 1),
            datetime_utc(2000, 1, 2),
        ]
    )
    def test_that_confirmation_timestamp_for_company_is_the_time_when_their_account_was_confirmed(
        self, expected_timestamp: datetime
    ) -> None:
        company_email = "test@test.test"
        self.datetime_service.freeze_time(expected_timestamp - timedelta(days=1))
        company = self.company_generator.create_company(
            confirmed=False, email=company_email
        )
        self.datetime_service.freeze_time(expected_timestamp)
        self._confirm_company(company_email)
        self.datetime_service.advance_time(timedelta(days=1))
        request = get_user_account_details.Request(user_id=company)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert (
            response.user_info.email_address_confirmation_timestamp
            == expected_timestamp
        )

    def test_that_current_time_is_returned(self) -> None:
        expected_time = self.datetime_service.now()
        self.datetime_service.freeze_time(expected_time)
        member = self.member_generator.create_member()
        request = get_user_account_details.Request(user_id=member)
        response = self.interactor.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.current_time == expected_time
        assert response.user_info.current_time.tzinfo == UTC

    def _confirm_member(self, member_email: str) -> None:
        response = self.confirm_member_interactor.confirm_member(
            request=confirm_member.ConfirmMemberInteractor.Request(
                email_address=member_email
            )
        )
        assert response.is_confirmed

    def _confirm_company(self, company_email: str) -> None:
        response = self.confirm_company_interactor.confirm_company(
            request=confirm_company.ConfirmCompanyInteractor.Request(
                email_address=company_email
            )
        )
        assert response.is_confirmed
