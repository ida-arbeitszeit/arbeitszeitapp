from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.repositories import PlanRepository, TransactionRepository


@inject
@dataclass
class GrantCredit:
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting
    datetime_service: DatetimeService
    plan_repository: PlanRepository

    def __call__(self, plan: Plan):
        """Social Accounting grants credit to Company after plan has been approved."""
        assert plan.approved, "Plan has not been approved!"

        payout_factor = self._calculate_payout_factor()

        accounts_and_amounts = [
            (plan.planner.means_account, plan.production_costs.means_cost),
            (plan.planner.raw_material_account, plan.production_costs.resource_cost),
            (
                plan.planner.work_account,
                payout_factor * plan.production_costs.labour_cost,
            ),
            (
                plan.planner.product_account,
                -plan.expected_sales_value(),
            ),
        ]

        for account, amount in accounts_and_amounts:
            transaction = self.transaction_repository.create_transaction(
                date=self.datetime_service.now(),
                account_from=self.social_accounting.account,
                account_to=account,
                amount=round(amount, 2),
                purpose=f"Plan-Id: {plan.id}",
            )
            transaction.adjust_balances()

    def _calculate_payout_factor(self) -> Decimal:
        """
        FIK = (A − ( P o + R o )) / (A + A o)
        """
        productive_plans = (
            self.plan_repository.all_productive_plans_approved_and_not_expired()
        )
        sum_of_productive_work_per_day = Decimal(0)
        for p in productive_plans:
            work_per_day = p.production_costs.labour_cost / p.timeframe
            sum_of_productive_work_per_day += work_per_day

        print("A", sum_of_productive_work_per_day)

        public_plans = self.plan_repository.all_public_plans_approved_and_not_expired()
        sum_of_public_work_per_day = Decimal(0)
        for p in public_plans:
            work_per_day = p.production_costs.labour_cost / p.timeframe
            sum_of_public_work_per_day += work_per_day

        print("A o", sum_of_public_work_per_day)

        sum_of_public_means_of_production_per_day = Decimal(0)
        for p in public_plans:
            means_of_production_per_day = p.production_costs.means_cost / p.timeframe
            sum_of_public_means_of_production_per_day += means_of_production_per_day

        print("P o", sum_of_public_means_of_production_per_day)

        sum_of_public_raw_materials_per_day = Decimal(0)
        for p in public_plans:
            raw_materials_per_day = p.production_costs.resource_cost / p.timeframe
            sum_of_public_raw_materials_per_day += raw_materials_per_day

        print("R o", sum_of_public_raw_materials_per_day)

        payout_factor = (
            sum_of_productive_work_per_day
            - (
                sum_of_public_means_of_production_per_day
                + sum_of_public_raw_materials_per_day
            )
        ) / (sum_of_productive_work_per_day + sum_of_public_work_per_day)
        print("factor", payout_factor)

        return Decimal(payout_factor)
