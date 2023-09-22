from uuid import uuid4

from arbeitszeit.email_notifications import AccountantNotificationAboutNewPlan
from arbeitszeit_web.email.notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)
from tests.email import FakeAddressBook, FakeEmailConfiguration
from tests.text_renderer import TextRendererImpl
from tests.www.base_test_case import BaseTestCase

Notification = AccountantNotificationAboutNewPlan


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(NotifyAccountantsAboutNewPlanPresenterImpl)
        self.address_book = self.injector.get(FakeAddressBook)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.text_renderer = self.injector.get(TextRendererImpl)

    def test_that_an_email_gets_sent(self) -> None:
        notification = Notification(
            product_name="test product", plan_id=uuid4(), accountant_id=uuid4()
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert self.email_service.sent_mails

    def test_that_email_gets_sent_to_correct_address(self) -> None:
        user = uuid4()
        notification = Notification(
            product_name="test product", plan_id=uuid4(), accountant_id=user
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert (
            self.address_book.get_user_email_address(user)
            in self.email_service.sent_mails[0].recipients
        )

    def test_that_email_gets_sent_to_only_one_recipient(self) -> None:
        notification = Notification(
            product_name="test product", plan_id=uuid4(), accountant_id=uuid4()
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert len(self.email_service.sent_mails[0].recipients) == 1

    def test_that_no_email_gets_sent_if_user_email_address_cannot_be_retrieved(
        self,
    ) -> None:
        user = uuid4()
        self.address_book.blacklist_user(user)
        notification = Notification(
            product_name="test product",
            plan_id=uuid4(),
            accountant_id=user,
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert not self.email_service.sent_mails

    def test_that_subject_line_is_correct(self) -> None:
        notification = Notification(
            product_name="test product", plan_id=uuid4(), accountant_id=uuid4()
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert self.email_service.sent_mails[0].subject == self.translator.gettext(
            "Plan was filed"
        )

    def test_sender_is_set_correctly(self) -> None:
        notification = Notification(
            product_name="test product", plan_id=uuid4(), accountant_id=uuid4()
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert (
            self.email_service.sent_mails[0].sender
            == self.email_configuration.get_sender_address()
        )

    def test_that_correct_text_template_is_rendered(self) -> None:
        notification = Notification(
            product_name="test product", plan_id=uuid4(), accountant_id=uuid4()
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert self.email_service.sent_mails[
            0
        ].html == self.text_renderer.render_accountant_notification_about_new_plan(
            product_name="test product",
        )
