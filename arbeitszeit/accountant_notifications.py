from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.presenters import NotifyAccountantsAboutNewPlanPresenter as Presenter
from arbeitszeit.repositories import AccountantRepository


@dataclass
class AccountantNotifier:
    presenter: Presenter
    accountant_repository: AccountantRepository

    def notify_all_accountants_about_new_plan(
        self, product_name: str, plan_id: UUID
    ) -> None:
        for accountant in self.accountant_repository.get_accountants():
            self.presenter.notify_accountant_about_new_plan(
                Presenter.Notification(
                    product_name=product_name,
                    plan_id=plan_id,
                    accountant_id=accountant.id,
                )
            )
