from dataclasses import dataclass
from typing import List

from arbeitszeit.email_notifications import RejectedPlanNotification
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator


@dataclass
class CompanyNotifier:
    email_sender: MailService
    translator: Translator
    database: DatabaseGateway
    text_renderer: TextRenderer
    email_configuration: EmailConfiguration

    def notify_planning_company_about_rejected_plan(
        self, notification: RejectedPlanNotification
    ) -> None:
        self._send_email(
            subject="Your plan was rejected",
            recipients=[notification.planner_email_address],
            html_content=self.text_renderer.render_company_notification_about_rejected_plan(
                company_name=notification.planning_company_name,
                product_name=notification.product_name,
                plan_id=str(notification.plan_id),
            ),
        )

    def _send_email(
        self, subject: str, recipients: List[str], html_content: str
    ) -> None:
        self.email_sender.send_message(
            self.translator.gettext(subject),
            recipients,
            html_content,
            self.email_configuration.get_sender_address(),
        )
