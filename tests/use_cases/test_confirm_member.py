from uuid import uuid4

from arbeitszeit.use_cases.confirm_member import ConfirmMemberUseCase as UseCase
from tests.token import TokenDeliveryService

from .base_test_case import BaseTestCase


class ConfirmMemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.token_deliverer = self.injector.get(TokenDeliveryService)

    def test_cannot_confirm_random_user_data_and_token(self) -> None:
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                member=uuid4(),
                token="",
            )
        )
        assert not response.is_confirmed

    def test_can_confirm_unconfirmed_member_with_valid_token(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        token = self.token_deliverer.presented_member_tokens[-1].token
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                member=member,
                token=token,
            )
        )
        assert response.is_confirmed

    def test_cannot_confirm_unconfirmed_member_with_invalid_token(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                member=member,
                token="123",
            )
        )
        assert not response.is_confirmed

    def test_cannot_confirm_member_with_token_for_other_member(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        self.member_generator.create_member(confirmed=False)
        wrong_token = self.token_deliverer.presented_member_tokens[-1].token
        response = self.use_case.confirm_member(
            request=UseCase.Request(
                member=member,
                token=wrong_token,
            )
        )
        assert not response.is_confirmed

    def test_cannot_confirm_member_twice(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        token = self.token_deliverer.presented_member_tokens[-1].token
        request = UseCase.Request(
            member=member,
            token=token,
        )
        self.use_case.confirm_member(request=request)
        response = self.use_case.confirm_member(request=request)
        assert not response.is_confirmed
