from arbeitszeit.interactors.confirm_member import ConfirmMemberInteractor as Interactor

from .base_test_case import BaseTestCase


class ConfirmMemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(Interactor)

    def test_cannot_confirm_random_email_address(self) -> None:
        response = self.interactor.confirm_member(
            request=Interactor.Request(email_address="test@test.test")
        )
        assert not response.is_confirmed

    def test_that_no_member_id_is_returned_when_email_address_is_invalid(self) -> None:
        response = self.interactor.confirm_member(
            request=Interactor.Request(email_address="test@test.test")
        )
        assert response.member is None

    def test_can_confirm_unconfirmed_member_with_valid_email_address(self) -> None:
        expected_email_address = "test@test.test"
        self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        response = self.interactor.confirm_member(
            request=Interactor.Request(email_address=expected_email_address)
        )
        assert response.is_confirmed

    def test_valid_email_address_returns_associated_user_id(self) -> None:
        expected_email_address = "test@cp.org"
        member = self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        response = self.interactor.confirm_member(
            request=Interactor.Request(email_address=expected_email_address)
        )
        assert response.member == member

    def test_cannot_confirm_unconfirmed_member_with_invalid_email_address(self) -> None:
        self.member_generator.create_member(confirmed=False)
        response = self.interactor.confirm_member(
            request=Interactor.Request(email_address="other@email.address")
        )
        assert not response.is_confirmed

    def test_cannot_confirm_member_twice(self) -> None:
        expected_email_address = "test@test.test"
        self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        request = Interactor.Request(email_address=expected_email_address)
        self.interactor.confirm_member(request=request)
        response = self.interactor.confirm_member(request=request)
        assert not response.is_confirmed
