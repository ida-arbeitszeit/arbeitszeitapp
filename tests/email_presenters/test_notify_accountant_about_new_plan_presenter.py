from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.email_notifications import AccountantNotificationAboutNewPlan
from arbeitszeit_web.email.notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)
from tests.email import FakeEmailConfiguration
from tests.text_renderer import TextRendererImpl
from tests.www.base_test_case import BaseTestCase

Notification = AccountantNotificationAboutNewPlan


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(NotifyAccountantsAboutNewPlanPresenterImpl)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.text_renderer = self.injector.get(TextRendererImpl)

    def test_that_an_email_gets_sent(self) -> None:
        notification = self.create_notification()
        self.presenter.notify_accountant_about_new_plan(notification)
        assert self.email_service.sent_mails

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_email_gets_sent_to_correct_address(
        self, expected_email_address: str
    ) -> None:
        notification = self.create_notification(email_address=expected_email_address)
        self.presenter.notify_accountant_about_new_plan(notification)
        assert expected_email_address in self.email_service.sent_mails[0].recipients

    def test_that_email_gets_sent_to_only_one_recipient(self) -> None:
        notification = self.create_notification()
        self.presenter.notify_accountant_about_new_plan(notification)
        assert len(self.email_service.sent_mails[0].recipients) == 1

    def test_that_subject_line_is_correct(self) -> None:
        notification = self.create_notification()
        self.presenter.notify_accountant_about_new_plan(notification)
        assert self.email_service.sent_mails[0].subject == self.translator.gettext(
            "Plan was filed"
        )

    def test_sender_is_set_correctly(self) -> None:
        notification = self.create_notification()
        self.presenter.notify_accountant_about_new_plan(notification)
        assert (
            self.email_service.sent_mails[0].sender
            == self.email_configuration.get_sender_address()
        )

    @parameterized.expand(
        [
            (
                "test product",
                "test accountant name",
            ),
            (
                "other product",
                "other accountant name",
            ),
        ]
    )
    def test_that_correct_text_template_is_rendered(
        self, product_name: str, accountant_name: str
    ) -> None:
        notification = self.create_notification(
            product_name=product_name, accountant_name=accountant_name
        )
        self.presenter.notify_accountant_about_new_plan(notification)
        assert self.email_service.sent_mails[
            0
        ].html == self.text_renderer.render_accountant_notification_about_new_plan(
            product_name=product_name,
            accountant_name=accountant_name,
        )

    def create_notification(
        self,
        email_address: str = "test@test.test",
        product_name: str = "test product",
        accountant_name: str = "test accountant",
    ) -> Notification:
        return Notification(
            product_name=product_name,
            plan_id=uuid4(),
            accountant_email_address=email_address,
            accountant_name=accountant_name,
        )
