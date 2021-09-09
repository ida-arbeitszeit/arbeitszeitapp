from dataclasses import dataclass
import datetime
from decimal import Decimal

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import SocialAccounting
from arbeitszeit.repositories import PlanRepository, TransactionRepository


@inject
@dataclass
class SynchronizedPlanActivation:
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting

    def __call__(self) -> None:
        self._grant_credit_and_activate_new_plans()
        self._payout_work_certificates(self._calculate_payout_factor())

    def _grant_credit_and_activate_new_plans(self) -> None:
        """
        Grant credit to planners of plans suitable for activation.
        Set these plans as active.
        """
        new_plans = self.plan_repository.get_plans_suitable_for_activation()

        for plan in new_plans:
            assert plan.approved, "Plan has not been approved!"
            assert not plan.is_active, "Plan is already active!"
            assert not plan.expired, "Plan is already expired!"

            accounts_and_amounts = [
                (plan.planner.means_account, plan.production_costs.means_cost),
                (
                    plan.planner.raw_material_account,
                    plan.production_costs.resource_cost,
                ),
                (
                    plan.planner.product_account,
                    -plan.expected_sales_value(),
                ),
            ]

            for account, amount in accounts_and_amounts:
                self.transaction_repository.create_transaction(
                    date=self.datetime_service.now(),
                    account_from=self.social_accounting.account,
                    account_to=account,
                    amount=round(amount, 2),
                    purpose=f"Plan-Id: {plan.id}",
                )

            self.plan_repository.activate_plan(plan, self.datetime_service.now())

    def _calculate_payout_factor(self) -> Decimal:
        """
        payout factor = (A − ( P o + R o )) / (A + A o)
        """
        # A
        productive_plans = (
            self.plan_repository.all_productive_plans_approved_active_and_not_expired()
        )
        sum_of_productive_work_per_day = Decimal(0)
        for p in productive_plans:
            work_per_day = p.production_costs.labour_cost / p.timeframe
            sum_of_productive_work_per_day += work_per_day

        # A_o
        public_plans = (
            self.plan_repository.all_public_plans_approved_active_and_not_expired()
        )
        sum_of_public_work_per_day = Decimal(0)
        for p in public_plans:
            work_per_day = p.production_costs.labour_cost / p.timeframe
            sum_of_public_work_per_day += work_per_day

        # P_o
        public_plans = (
            self.plan_repository.all_public_plans_approved_active_and_not_expired()
        )
        sum_of_public_means_of_production_per_day = Decimal(0)
        for p in public_plans:
            means_of_production_per_day = p.production_costs.means_cost / p.timeframe
            sum_of_public_means_of_production_per_day += means_of_production_per_day

        # R_o
        public_plans = (
            self.plan_repository.all_public_plans_approved_active_and_not_expired()
        )
        sum_of_public_raw_materials_per_day = Decimal(0)
        for p in public_plans:
            raw_materials_per_day = p.production_costs.resource_cost / p.timeframe
            sum_of_public_raw_materials_per_day += raw_materials_per_day

        # Payout factor
        numerator = sum_of_productive_work_per_day - (
            sum_of_public_means_of_production_per_day
            + sum_of_public_raw_materials_per_day
        )
        denominator = (sum_of_productive_work_per_day + sum_of_public_work_per_day) or 1
        payout_factor = numerator / denominator
        print(payout_factor)
        return Decimal(payout_factor)

    def _payout_work_certificates(self, payout_factor: Decimal) -> None:
        """
        The payout amount equals to payout factor times labour costs per day.
        """

        for plan in self.plan_repository.all_plans_approved_active_and_not_expired():
            assert plan.approved, "Plan has not been approved!"
            assert plan.is_active, "Plan is not active"
            assert not plan.expired, "Plan is expired"

            if plan.last_certificate_payout:
                # if last payout was today
                last_payout = plan.last_certificate_payout
                today = self.datetime_service.today()
                if (last_payout.year, last_payout.month, last_payout.day) == (
                    today.year,
                    today.month,
                    today.day,
                ):
                    continue

            account_to = plan.planner.work_account
            amount = payout_factor * plan.production_costs.labour_cost / plan.timeframe

            self.transaction_repository.create_transaction(
                date=self.datetime_service.now(),
                account_from=self.social_accounting.account,
                account_to=account_to,
                amount=round(amount, 2),
                purpose=f"Plan-Id: {plan.id}",
            )

            self.plan_repository.set_last_certificate_payout(
                plan, self.datetime_service.now()
            )
