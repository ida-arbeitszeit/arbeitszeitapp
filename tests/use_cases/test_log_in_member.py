from typing import Optional

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit.use_cases.register_member import RegisterMemberUseCase

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(LogInMemberUseCase)
        self.register_use_case = self.injector.get(RegisterMemberUseCase)

    def test_that_with_no_members_present_cannot_log_in(self) -> None:
        request = self.get_request()
        response = self.use_case.log_in_member(request)
        self.assertFalse(response.is_logged_in)

    def test_that_with_correct_credentials_can_log_in(self) -> None:
        email = "test user email"
        password = "test user password"
        self.create_member(email=email, password=password)
        request = self.get_request(email=email, password=password)
        response = self.use_case.log_in_member(request)
        self.assertTrue(response.is_logged_in)

    def test_with_invalid_email_address_return_a_rejection_reason(self) -> None:
        request = self.get_request()
        response = self.use_case.log_in_member(request)
        self.assertTrue(response.rejection_reason)

    def test_with_invalid_email_address_return_correct_rejection_reason(self) -> None:
        request = self.get_request()
        response = self.use_case.log_in_member(request)
        self.assertEqual(
            response.rejection_reason,
            LogInMemberUseCase.RejectionReason.unknown_email_address,
        )

    def test_with_invalid_password_return_correct_rejection_reason(self) -> None:
        email = "test user email"
        self.create_member(email=email, password="correct password")
        request = self.get_request(email=email, password="incorrect password")
        response = self.use_case.log_in_member(request)
        self.assertEqual(
            response.rejection_reason,
            LogInMemberUseCase.RejectionReason.invalid_password,
        )

    def test_with_successful_login_give_no_rejection_reason(self) -> None:
        email = "test user email"
        password = "test user password"
        self.create_member(email=email, password=password)
        request = self.get_request(email=email, password=password)
        response = self.use_case.log_in_member(request)
        self.assertIsNone(response.rejection_reason)

    def test_that_email_in_response_is_email_from_request(self) -> None:
        email_addresses = [
            "test@test.test",
            "test2@test.test",
        ]
        for expected_email in email_addresses:
            with self.subTest():
                request = self.get_request(email=expected_email)
                response = self.use_case.log_in_member(request)
                self.assertEqual(response.email, expected_email)

    def test_that_correct_user_id_is_returned_on_successful_login(self) -> None:
        password = "testpassword"
        email = "test@test.test"
        member = self.member_generator.create_member(
            email=email,
            password=password,
        )
        request = self.get_request(
            email=email,
            password=password,
        )
        response = self.use_case.log_in_member(request)
        assert response.user_id == member

    def test_that_no_user_id_is_returned_on_invalid_login(self) -> None:
        request = self.get_request(
            email="random@email.com",
            password="12341234",
        )
        response = self.use_case.log_in_member(request)
        assert response.user_id is None

    def get_request(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> LogInMemberUseCase.Request:
        if email is None:
            email = "test@test.test"
        if password is None:
            password = "test password"
        return LogInMemberUseCase.Request(
            email=email,
            password=password,
        )

    def create_member(self, email: str, password: str) -> None:
        name = "test user name"
        response = self.register_use_case.register_member(
            request=RegisterMemberUseCase.Request(
                email=email,
                name=name,
                password=password,
            )
        )
        assert not response.is_rejected
