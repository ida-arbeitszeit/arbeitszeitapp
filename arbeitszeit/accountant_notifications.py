from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import AccountantRepository


@dataclass
class Notification:
    product_name: str
    plan_id: UUID
    accountant_id: UUID


class NotifyAccountantsAboutNewPlanPresenter(Protocol):
    def notify_accountant_about_new_plan(self, notification: Notification) -> None:
        ...


@inject
@dataclass
class AccountantNotifier:
    presenter: NotifyAccountantsAboutNewPlanPresenter
    accountant_repository: AccountantRepository

    def notify_all_accountants_about_new_plan(
        self, product_name: str, plan_id: UUID
    ) -> None:
        for accountant in self.accountant_repository.get_all_accountants():
            self.presenter.notify_accountant_about_new_plan(
                Notification(
                    product_name=product_name,
                    plan_id=plan_id,
                    accountant_id=accountant.id,
                )
            )
