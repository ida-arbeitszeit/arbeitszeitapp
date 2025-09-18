from uuid import uuid4

from arbeitszeit import email_notifications
from arbeitszeit.interactors.resend_confirmation_mail import (
    ResendConfirmationMailInteractor as Interactor,
)

from .base_test_case import BaseTestCase


class MemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(Interactor)

    def test_that_token_will_be_sent_for_unconfirmed_member(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        response = self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=member)
        )
        assert response.is_token_sent

    def test_that_token_wont_be_sent_for_confirmed_member(self) -> None:
        member = self.member_generator.create_member(confirmed=True)
        response = self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=member)
        )
        assert not response.is_token_sent

    def test_that_confirmation_message_is_sent_out_for_unconfirmed_member(self) -> None:
        member = self.member_generator.create_member(confirmed=False)
        tokens_delivered_so_far = len(self.delivered_registration_messages())
        self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=member)
        )
        assert (
            len(self.delivered_registration_messages()) == tokens_delivered_so_far + 1
        )

    def delivered_registration_messages(
        self,
    ) -> list[email_notifications.MemberRegistration]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.MemberRegistration)
        ]


class NoValidUserTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(Interactor)

    def test_that_token_cannot_be_sent_for_random_uuid(self) -> None:
        response = self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=uuid4())
        )
        assert not response.is_token_sent


class CompanyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(Interactor)

    def test_can_resend_confirmation_email_for_unapproved_companies(self) -> None:
        company = self.company_generator.create_company(confirmed=False)
        response = self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=company)
        )
        assert response.is_token_sent

    def test_cannnot_resend_confirmation_email_for_approved_companies(self) -> None:
        company = self.company_generator.create_company(confirmed=True)
        response = self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=company)
        )
        assert not response.is_token_sent

    def test_that_confirmation_message_is_sent_out_for_unconfirmed_company(
        self,
    ) -> None:
        company = self.company_generator.create_company(confirmed=False)
        tokens_delivered_so_far = len(self.delivered_registration_messages())
        self.interactor.resend_confirmation_mail(
            request=Interactor.Request(user=company)
        )
        assert (
            len(self.delivered_registration_messages()) == tokens_delivered_so_far + 1
        )

    def delivered_registration_messages(
        self,
    ) -> list[email_notifications.CompanyRegistration]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.CompanyRegistration)
        ]
