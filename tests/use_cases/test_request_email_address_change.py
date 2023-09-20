from parameterized import parameterized

from arbeitszeit import email_notifications
from arbeitszeit.use_cases import request_email_address_change as use_case

from .base_test_case import BaseTestCase


class RequestEmailAddressChangeTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(use_case.RequestEmailAddressChangeUseCase)

    @parameterized.expand(
        [
            ("test@test.test", "new@test.test"),
            ("a@b.c", "d@b.c"),
        ]
    )
    def test_that_request_is_rejected_for_unknown_email_address(
        self, current: str, new: str
    ) -> None:
        request = use_case.Request(
            current_email_address=current,
            new_email_address=new,
        )
        response = self.use_case.request_email_address_change(request)
        assert response.is_rejected

    def test_that_confirmed_members_requests_are_accepted(self) -> None:
        member_email_address = "test@test.test"
        new_email_address = "new@test.test"
        self.member_generator.create_member(email=member_email_address, confirmed=True)
        request = use_case.Request(
            current_email_address=member_email_address,
            new_email_address=new_email_address,
        )
        response = self.use_case.request_email_address_change(request)
        assert not response.is_rejected

    def test_that_confirmed_companies_requests_are_accepted(self) -> None:
        company_email_address = "test@test.test"
        new_email_address = "new@test.test"
        self.company_generator.create_company(
            email=company_email_address, confirmed=True
        )
        request = use_case.Request(
            current_email_address=company_email_address,
            new_email_address=new_email_address,
        )
        response = self.use_case.request_email_address_change(request)
        assert not response.is_rejected

    def test_that_accountants_requests_are_accepted(self) -> None:
        accountant_email_address = "test@test.test"
        new_email_address = "new@test.test"
        self.accountant_generator.create_accountant(
            email_address=accountant_email_address
        )
        request = use_case.Request(
            current_email_address=accountant_email_address,
            new_email_address=new_email_address,
        )
        response = self.use_case.request_email_address_change(request)
        assert not response.is_rejected

    def test_that_requests_are_rejected_if_new_email_address_is_already_taken_by_member(
        self,
    ) -> None:
        old_email_address = "test@test.test"
        new_email_address = "new@test.test"
        self.member_generator.create_member(email=old_email_address)
        self.member_generator.create_member(email=new_email_address)
        request = use_case.Request(
            current_email_address=old_email_address,
            new_email_address=new_email_address,
        )
        response = self.use_case.request_email_address_change(request)
        assert response.is_rejected

    @parameterized.expand(
        [
            ("",),
            ("word",),
            ("a@",),
            ("@b",),
        ]
    )
    def test_that_email_addresses_that_are_definityly_not_valid_are_rejected_as_new_addresses(
        self, invalid: str
    ) -> None:
        original_email_address = "test@test.test"
        self.member_generator.create_member(email=original_email_address)
        request = use_case.Request(
            current_email_address=original_email_address,
            new_email_address=invalid,
        )
        response = self.use_case.request_email_address_change(request)
        assert response.is_rejected

    def test_that_change_confirmation_was_presented_after_successful_request_of_member(
        self,
    ) -> None:
        original_address = "test@test.test"
        new_address = "new@test.test"
        self.member_generator.create_member(email=original_address)
        request = use_case.Request(
            current_email_address=original_address,
            new_email_address=new_address,
        )
        self.use_case.request_email_address_change(request)
        assert self.delivered_notifications()

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_delivered_notification_contains_current_email_address_as_requested(
        self, original_address: str
    ) -> None:
        self.member_generator.create_member(email=original_address)
        new_address = "new@test.test"
        request = use_case.Request(
            current_email_address=original_address,
            new_email_address=new_address,
        )
        self.use_case.request_email_address_change(request)
        notification = self.get_latest_notification_delivered()
        assert notification.old_email_address == original_address

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_delivered_notification_contains_new_email_address_as_requested(
        self, new_address: str
    ) -> None:
        original_address = "origional@test.test"
        self.member_generator.create_member(email=original_address)
        request = use_case.Request(
            current_email_address=original_address,
            new_email_address=new_address,
        )
        self.use_case.request_email_address_change(request)
        notification = self.get_latest_notification_delivered()
        assert notification.new_email_address == new_address

    def test_that_no_notifiation_is_delivered_if_email_address_is_unkown(self) -> None:
        request = use_case.Request(
            current_email_address="test@test.test",
            new_email_address="new@test.test",
        )
        self.use_case.request_email_address_change(request)
        assert not self.delivered_notifications()

    def get_latest_notification_delivered(
        self,
    ) -> email_notifications.EmailChangeConfirmation:
        notifications = self.delivered_notifications()
        assert notifications
        return notifications[-1]

    def delivered_notifications(
        self,
    ) -> list[email_notifications.EmailChangeConfirmation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.EmailChangeConfirmation)
        ]
