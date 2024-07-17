from parameterized import parameterized

from arbeitszeit import email_notifications
from arbeitszeit.use_cases import request_email_address_change as use_case

from .base_test_case import BaseTestCase


def create_use_case_request(
    current_email_address: str,
    new_email_address: str,
    current_password: str,
) -> use_case.Request:
    return use_case.Request(
        current_email_address=current_email_address,
        new_email_address=new_email_address,
        current_password=current_password,
    )


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
        request = create_use_case_request(
            current_email_address=current,
            new_email_address=new,
            current_password="some_pw",
        )
        response = self.use_case.request_email_address_change(request)
        assert (
            response.rejection_reason
            == response.RejectionReason.current_email_address_does_not_exist
        )

    def test_that_confirmed_members_requests_are_accepted(self) -> None:
        member_email_address = "test@test.test"
        current_password = "some_password"
        new_email_address = "new@test.test"
        self.member_generator.create_member(
            email=member_email_address, password=current_password, confirmed=True
        )
        request = create_use_case_request(
            current_email_address=member_email_address,
            new_email_address=new_email_address,
            current_password=current_password,
        )
        response = self.use_case.request_email_address_change(request)
        assert not response.rejection_reason

    def test_that_confirmed_companies_requests_are_accepted(self) -> None:
        company_email_address = "test@test.test"
        current_password = "some_password"
        new_email_address = "new@test.test"
        self.company_generator.create_company(
            email=company_email_address, password=current_password, confirmed=True
        )
        request = create_use_case_request(
            current_email_address=company_email_address,
            new_email_address=new_email_address,
            current_password=current_password,
        )
        response = self.use_case.request_email_address_change(request)
        assert not response.rejection_reason

    def test_that_accountants_requests_are_accepted(self) -> None:
        accountant_email_address = "test@test.test"
        current_password = "some_password"
        new_email_address = "new@test.test"
        self.accountant_generator.create_accountant(
            email_address=accountant_email_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=accountant_email_address,
            new_email_address=new_email_address,
            current_password=current_password,
        )
        response = self.use_case.request_email_address_change(request)
        assert not response.rejection_reason

    def test_that_requests_are_rejected_if_new_email_address_is_already_taken_by_member(
        self,
    ) -> None:
        current_email_address = "test@test.test"
        current_password = "some_password"
        new_email_address = "new@test.test"
        self.member_generator.create_member(
            email=current_email_address, password=current_password
        )
        self.member_generator.create_member(email=new_email_address)
        request = create_use_case_request(
            current_email_address=current_email_address,
            new_email_address=new_email_address,
            current_password=current_password,
        )
        response = self.use_case.request_email_address_change(request)
        assert (
            response.rejection_reason
            == response.RejectionReason.new_email_address_already_taken
        )

    @parameterized.expand(
        [
            ("",),
            ("word",),
            ("a@",),
            ("@b",),
        ]
    )
    def test_that_email_addresses_that_are_definitely_not_valid_are_rejected_as_new_addresses(
        self, invalid: str
    ) -> None:
        original_email_address = "test@test.test"
        current_password = "some_password"
        self.member_generator.create_member(
            email=original_email_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=original_email_address,
            new_email_address=invalid,
            current_password=current_password,
        )
        response = self.use_case.request_email_address_change(request)
        assert (
            response.rejection_reason == response.RejectionReason.invalid_email_address
        )

    @parameterized.expand(
        [
            ("pw_1", "pw1"),
            ("", "pw1"),
            ("pw_1", ""),
        ]
    )
    def test_that_request_is_rejected_if_passwords_do_not_match(
        self, correct_password: str, submitted_password: str
    ) -> None:
        member_email_address = "test@test.test"
        new_email_address = "new@test.test"
        self.member_generator.create_member(
            email=member_email_address, password=correct_password, confirmed=True
        )
        request = create_use_case_request(
            current_email_address=member_email_address,
            new_email_address=new_email_address,
            current_password=submitted_password,
        )
        response = self.use_case.request_email_address_change(request)
        assert response.rejection_reason == response.RejectionReason.incorrect_password


class RequestEmailAddressChangeNotificationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(use_case.RequestEmailAddressChangeUseCase)

    def test_that_change_warning_mail_is_sent_after_successful_request_of_member(
        self,
    ) -> None:
        original_address = "test@test.test"
        current_password = "some_password"
        new_address = "new@test.test"
        self.member_generator.create_member(
            email=original_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=original_address,
            new_email_address=new_address,
            current_password=current_password,
        )
        self.use_case.request_email_address_change(request)
        assert len(self.delivered_change_warning_notifications()) == 1

    def test_that_change_confirmation_mail_is_sent_after_successful_request_of_member(
        self,
    ) -> None:
        original_address = "test@test.test"
        current_password = "some_password"
        new_address = "new@test.test"
        self.member_generator.create_member(
            email=original_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=original_address,
            new_email_address=new_address,
            current_password=current_password,
        )
        self.use_case.request_email_address_change(request)
        assert len(self.delivered_change_confirmation_notifications()) == 1

    def test_that_the_warning_mail_contains_original_address_as_requested(
        self,
    ) -> None:
        original_address = "test@test.test"
        current_password = "some_password"
        new_address = "new@test.test"
        self.member_generator.create_member(
            email=original_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=original_address,
            new_email_address=new_address,
            current_password=current_password,
        )
        self.use_case.request_email_address_change(request)
        notification = self.delivered_change_warning_notifications()[0]
        assert notification.old_email_address == original_address

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_change_confirmation_mail_contains_current_email_address_as_requested(
        self, original_address: str
    ) -> None:
        current_password = "some_password"
        new_address = "new@test.test"
        self.member_generator.create_member(
            email=original_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=original_address,
            new_email_address=new_address,
            current_password=current_password,
        )
        self.use_case.request_email_address_change(request)
        notification = self.delivered_change_confirmation_notifications()[0]
        assert notification.old_email_address == original_address

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_change_confirmation_mail_contains_new_email_address_as_requested(
        self, new_address: str
    ) -> None:
        original_address = "origional@test.test"
        current_password = "some_password"
        self.member_generator.create_member(
            email=original_address, password=current_password
        )
        request = create_use_case_request(
            current_email_address=original_address,
            new_email_address=new_address,
            current_password=current_password,
        )
        self.use_case.request_email_address_change(request)
        notification = self.delivered_change_confirmation_notifications()[0]
        assert notification.new_email_address == new_address

    def test_that_no_notifications_are_delivered_if_email_address_is_unkown(
        self,
    ) -> None:
        request = create_use_case_request(
            current_email_address="test@test.test",
            new_email_address="new@test.test",
            current_password="some_pw",
        )
        self.use_case.request_email_address_change(request)
        assert not self.delivered_change_confirmation_notifications()
        assert not self.delivered_change_warning_notifications()

    def test_that_no_notifications_are_delivered_if_passwords_are_not_matching(
        self,
    ) -> None:
        correct_password = "some password"
        submitted_password = correct_password + "x"
        member_email_address = "test@test.test"
        new_email_address = "new@test.test"
        self.member_generator.create_member(
            email=member_email_address, password=correct_password, confirmed=True
        )
        request = create_use_case_request(
            current_email_address=member_email_address,
            new_email_address=new_email_address,
            current_password=submitted_password,
        )
        self.use_case.request_email_address_change(request)
        assert not self.delivered_change_confirmation_notifications()
        assert not self.delivered_change_warning_notifications()

    def delivered_change_confirmation_notifications(
        self,
    ) -> list[email_notifications.EmailChangeConfirmation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.EmailChangeConfirmation)
        ]

    def delivered_change_warning_notifications(
        self,
    ) -> list[email_notifications.EmailChangeWarning]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.EmailChangeWarning)
        ]
