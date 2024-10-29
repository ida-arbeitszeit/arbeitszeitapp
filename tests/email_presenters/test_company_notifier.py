from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.email_notifications import RejectedPlanNotification
from arbeitszeit_web.email.company_notifier import CompanyNotifier
from tests.email import FakeEmailConfiguration
from tests.text_renderer import TextRendererImpl
from tests.www.base_test_case import BaseTestCase

Notification = RejectedPlanNotification


class CompanyNotifierTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_notifier = self.injector.get(CompanyNotifier)
        self.email_configuration = self.injector.get(FakeEmailConfiguration)
        self.text_renderer = self.injector.get(TextRendererImpl)

    def test_that_an_email_gets_sent(self) -> None:
        notification = self.create_notification()
        self.company_notifier.notify_planning_company_about_rejected_plan(notification)
        assert self.email_service.sent_mails

    def test_that_email_gets_sent_to_correct_address(self) -> None:
        notification = self.create_notification(email_address="email@address.com")
        self.company_notifier.notify_planning_company_about_rejected_plan(notification)
        assert "email@address.com" in self.email_service.sent_mails[0].recipients

    def test_that_subject_line_is_correct(self) -> None:
        notification = self.create_notification()
        self.company_notifier.notify_planning_company_about_rejected_plan(notification)
        assert self.email_service.sent_mails[0].subject == self.translator.gettext(
            "Your plan was rejected"
        )

    def test_sender_is_set_correctly(self) -> None:
        notification = self.create_notification()
        self.company_notifier.notify_planning_company_about_rejected_plan(notification)
        assert (
            self.email_service.sent_mails[0].sender
            == self.email_configuration.get_sender_address()
        )

    @parameterized.expand(
        [
            (
                "test company",
                "test product",
            ),
            (
                "other company",
                "other product",
            ),
        ]
    )
    def test_that_correct_text_template_is_rendered(
        self, company_name: str, product_name: str
    ) -> None:
        plan_id = uuid4()
        notification = self.create_notification(
            company_name=company_name, product_name=product_name, plan_id=plan_id
        )
        self.company_notifier.notify_planning_company_about_rejected_plan(notification)
        assert self.email_service.sent_mails[
            0
        ].html == self.text_renderer.render_company_notification_about_rejected_plan(
            company_name=company_name, product_name=product_name, plan_id=str(plan_id)
        )

    def create_notification(
        self,
        email_address: str = "test@test.test",
        company_name: str = "test company",
        product_name: str = "test product",
        plan_id: UUID = uuid4(),
    ) -> Notification:
        return Notification(
            product_name=product_name,
            plan_id=plan_id,
            planner_email_address=email_address,
            planning_company_name=company_name,
        )
