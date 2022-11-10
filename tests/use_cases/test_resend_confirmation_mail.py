from uuid import uuid4

from arbeitszeit.use_cases.resend_confirmation_mail import (
    ResendConfirmationMailUseCase as UseCase,
)
from tests.token import FakeTokenService, TokenDeliveryService

from .base_test_case import BaseTestCase


class MemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.token_presenter = self.injector.get(TokenDeliveryService)
        self.token_service = self.injector.get(FakeTokenService)

    def test_that_token_will_be_sent_for_unconfirmed_member(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        response = self.use_case.resend_confirmation_mail(
            request=UseCase.Request(user=member)
        )
        assert response.is_token_sent

    def test_that_token_wont_be_sent_for_confirmed_member(self) -> None:
        member = self.member_generator.create_member(confirmed=True)
        response = self.use_case.resend_confirmation_mail(
            request=UseCase.Request(user=member)
        )
        assert not response.is_token_sent

    def test_that_confirmation_message_is_sent_out_for_unconfirmed_member(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        tokens_delivered_so_far = len(self.token_presenter.presented_member_tokens)
        self.use_case.resend_confirmation_mail(request=UseCase.Request(user=member))
        assert (
            len(self.token_presenter.presented_member_tokens)
            == tokens_delivered_so_far + 1
        )

    def test_that_confirmation_message_is_sent_contains_valid_token(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        self.use_case.resend_confirmation_mail(request=UseCase.Request(user=member))
        assert self.token_service.confirm_token(
            self.token_presenter.presented_member_tokens[-1][1], 10000
        )

    def test_that_token_sent_to_member_is_valid_email_address(self) -> None:
        expected_email_address = "member@test.test"
        member = self.member_generator.create_member(
            confirmed=False, email=expected_email_address
        )
        self.use_case.resend_confirmation_mail(request=UseCase.Request(user=member))
        assert (
            self.token_service.confirm_token(
                self.token_presenter.presented_member_tokens[-1][1], 10000
            )
            == expected_email_address
        )


class NoValidUserTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)

    def test_that_token_cannot_be_sent_for_random_uuid(self) -> None:
        response = self.use_case.resend_confirmation_mail(
            request=UseCase.Request(user=uuid4())
        )
        assert not response.is_token_sent


class CompanyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.token_presenter = self.injector.get(TokenDeliveryService)
        self.token_service = self.injector.get(FakeTokenService)

    def test_can_resend_confirmation_email_for_unapproved_companies(self) -> None:
        company = self.company_generator.create_company(confirmed=False)
        response = self.use_case.resend_confirmation_mail(
            request=UseCase.Request(user=company)
        )
        assert response.is_token_sent

    def test_cannnot_resend_confirmation_email_for_approved_companies(self) -> None:
        company = self.company_generator.create_company(confirmed=True)
        response = self.use_case.resend_confirmation_mail(
            request=UseCase.Request(user=company)
        )
        assert not response.is_token_sent

    def test_that_confirmation_message_is_sent_out_for_unconfirmed_company(
        self,
    ) -> None:
        company = self.company_generator.create_company(confirmed=False)
        tokens_delivered_so_far = len(self.token_presenter.presented_company_tokens)
        self.use_case.resend_confirmation_mail(request=UseCase.Request(user=company))
        assert (
            len(self.token_presenter.presented_company_tokens)
            == tokens_delivered_so_far + 1
        )

    def test_that_confirmation_message_is_sent_contains_valid_token(self) -> None:
        company = self.company_generator.create_company(confirmed=False)
        self.use_case.resend_confirmation_mail(request=UseCase.Request(user=company))
        assert self.token_service.confirm_token(
            self.token_presenter.presented_company_tokens[-1][1], 10000
        )

    def test_that_token_sent_to_company_is_valid_email_address(self) -> None:
        expected_email_address = "company@test.test"
        company = self.company_generator.create_company(
            confirmed=False, email=expected_email_address
        )
        self.use_case.resend_confirmation_mail(request=UseCase.Request(user=company))
        assert (
            self.token_service.confirm_token(
                self.token_presenter.presented_company_tokens[-1][1], 10000
            )
            == expected_email_address
        )
