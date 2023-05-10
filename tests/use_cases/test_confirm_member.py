from arbeitszeit.use_cases.confirm_member import ConfirmMemberUseCase as UseCase
from tests.token import TokenDeliveryService

from .base_test_case import BaseTestCase


class ConfirmMemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.token_deliverer = self.injector.get(TokenDeliveryService)

    def test_cannot_confirm_random_email_address(self) -> None:
        response = self.use_case.confirm_member(
            request=UseCase.Request(email_address="test@test.test")
        )
        assert not response.is_confirmed

    def test_that_no_member_id_is_returned_when_email_address_is_invalid(self) -> None:
        response = self.use_case.confirm_member(
            request=UseCase.Request(email_address="test@test.test")
        )
        assert response.member is None

    def test_can_confirm_unconfirmed_member_with_valid_email_address(self) -> None:
        expected_email_address = "test@test.test"
        self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        response = self.use_case.confirm_member(
            request=UseCase.Request(email_address=expected_email_address)
        )
        assert response.is_confirmed

    def test_valid_email_address_returns_associated_user_id(self) -> None:
        expected_email_address = "test@cp.org"
        member = self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        response = self.use_case.confirm_member(
            request=UseCase.Request(email_address=expected_email_address)
        )
        assert response.member == member

    def test_cannot_confirm_unconfirmed_member_with_invalid_email_address(self) -> None:
        self.member_generator.create_member(confirmed=False)
        response = self.use_case.confirm_member(
            request=UseCase.Request(email_address="other@email.address")
        )
        assert not response.is_confirmed

    def test_cannot_confirm_member_twice(self) -> None:
        expected_email_address = "test@test.test"
        self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        request = UseCase.Request(email_address=expected_email_address)
        self.use_case.confirm_member(request=request)
        response = self.use_case.confirm_member(request=request)
        assert not response.is_confirmed
