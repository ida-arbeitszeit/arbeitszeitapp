from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.email_notifications import (
    AccountantNotificationAboutNewPlan,
    EmailSender,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class AccountantNotifier:
    email_sender: EmailSender
    database: DatabaseGateway

    def notify_all_accountants_about_new_plan(
        self, product_name: str, plan_id: UUID
    ) -> None:
        for (
            accountant,
            email,
        ) in self.database.get_accountants().joined_with_email_address():
            self.email_sender.send_email(
                AccountantNotificationAboutNewPlan(
                    product_name=product_name,
                    plan_id=plan_id,
                    accountant_name=accountant.name,
                    accountant_email_address=email.address,
                )
            )
