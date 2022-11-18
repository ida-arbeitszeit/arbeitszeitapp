from arbeitszeit.use_cases.confirm_member import ConfirmMemberUseCase as UseCase
from tests.token import TokenDeliveryService

from .base_test_case import BaseTestCase


class ConfirmMemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.token_deliverer = self.injector.get(TokenDeliveryService)

    def test_cannot_confirm_random_token(self) -> None:
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                token="",
            )
        )
        assert not response.is_confirmed

    def test_that_no_member_id_is_returned_when_token_is_invalid(self) -> None:
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                token="",
            )
        )
        assert response.member is None

    def test_can_confirm_unconfirmed_member_with_valid_token(self) -> None:
        self.member_generator.create_member(confirmed=False)
        token = self.token_deliverer.presented_member_tokens[-1].token
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                token=token,
            )
        )
        assert response.is_confirmed

    def test_valid_token_returns_associated_user_id(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        token = self.token_deliverer.presented_member_tokens[-1].token
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                token=token,
            )
        )
        assert response.member == member

    def test_cannot_confirm_unconfirmed_member_with_invalid_token(self) -> None:
        self.member_generator.create_member(confirmed=False)
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                token="123",
            )
        )
        assert not response.is_confirmed

    def test_cannot_confirm_member_twice(self) -> None:
        self.member_generator.create_member(confirmed=False)
        token = self.token_deliverer.presented_member_tokens[-1].token
        request = UseCase.Request(
            token=token,
        )
        self.use_case.confirm_member(request=request)
        response = self.use_case.confirm_member(request=request)
        assert not response.is_confirmed
