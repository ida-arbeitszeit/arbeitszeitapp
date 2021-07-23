from dataclasses import dataclass

from injector import inject

from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.repositories import TransactionRepository
from arbeitszeit.transaction_factory import TransactionFactory

from .adjust_balance import adjust_balance


@inject
@dataclass
class GrantCredit:
    transaction_repository: TransactionRepository
    transaction_factory: TransactionFactory
    social_accounting: SocialAccounting

    def __call__(self, plan: Plan):
        """Social Accounting grants credit after plan has been approved."""
        assert plan.approved, "Plan has not been approved!"
        social_accounting_account = self.social_accounting.account

        prd = plan.costs_p + plan.costs_r + plan.costs_a
        accounts_and_amounts = [
            (plan.planner.means_account, plan.costs_p),
            (plan.planner.raw_material_account, plan.costs_r),
            (plan.planner.work_account, plan.costs_a),
            (plan.planner.product_account, -prd),
        ]

        for account, amount in accounts_and_amounts:
            adjust_balance(account, amount)
            transaction = self.transaction_factory.create_transaction(
                account_from=social_accounting_account,
                account_to=account,
                amount=amount,
                purpose=f"Plan-Id: {plan.id}",
            )
            self.transaction_repository.add(transaction)
