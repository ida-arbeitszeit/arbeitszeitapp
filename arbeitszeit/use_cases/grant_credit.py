from dataclasses import dataclass

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.repositories import TransactionRepository


@inject
@dataclass
class GrantCredit:
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting
    datetime_service: DatetimeService

    def __call__(self, plan: Plan):
        """Social Accounting grants credit after plan has been approved."""
        assert plan.approved, "Plan has not been approved!"
        social_accounting_account = self.social_accounting.account

        accounts_and_amounts = [
            (plan.planner.means_account, plan.production_costs.means_cost),
            (plan.planner.raw_material_account, plan.production_costs.resource_cost),
            (plan.planner.work_account, plan.production_costs.labour_cost),
            (plan.planner.product_account, -plan.production_costs.total_cost()),
        ]

        for account, amount in accounts_and_amounts:
            self.transaction_repository.create_transaction(
                date=self.datetime_service.now(),
                account_from=social_accounting_account,
                account_to=account,
                amount=amount,
                purpose=f"Plan-Id: {plan.id}",
            )
