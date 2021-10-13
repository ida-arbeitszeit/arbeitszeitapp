from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Account, Plan, ProductionCosts, SocialAccounting
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
        self._payout_work_certificates()

    def _grant_credit_and_activate_new_plans(self) -> None:
        """
        Grant credit to planners of plans suitable for activation.
        Set these plans as active.
        """
        past_plan_activation_date = self.datetime_service.past_plan_activation_date()
        new_plans = self.plan_repository.get_approved_plans_created_before(
            past_plan_activation_date
        )
        for plan in new_plans:
            self._credit_production_cost_to_planner(plan)
            self.plan_repository.activate_plan(plan, self.datetime_service.now())

    def _payout_work_certificates(self) -> None:
        """
        The payout amount equals to payout factor times labour costs per day.
        Payout takes place once every day of a plan's planning cycle, except the last day.
        """
        payout_factor = self._calculate_payout_factor()
        for plan in self.plan_repository.all_plans_approved_active_and_not_expired():
            if self._last_certificate_payout_was_today(plan):
                continue
            if self._plan_expires_today(plan):
                continue
            amount = payout_factor * plan.production_costs.labour_cost / plan.timeframe
            self._create_transaction_from_social_accounting(
                plan, plan.planner.work_account, amount
            )
            self.plan_repository.set_last_certificate_payout(
                plan, self.datetime_service.now()
            )

    def _calculate_payout_factor(self) -> Decimal:
        # payout factor = (A − ( P o + R o )) / (A + A o)
        productive_plans = (
            self.plan_repository.all_productive_plans_approved_active_and_not_expired()
        )
        public_plans = (
            self.plan_repository.all_public_plans_approved_active_and_not_expired()
        )
        # A o, P o, R o
        public_costs_per_day: ProductionCosts = sum(
            (p.production_costs / p.timeframe for p in public_plans),
            start=ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
        )
        # A
        sum_of_productive_work_per_day = decimal_sum(
            p.production_costs.labour_cost / p.timeframe for p in productive_plans
        )
        numerator = sum_of_productive_work_per_day - (
            public_costs_per_day.means_cost + public_costs_per_day.resource_cost
        )
        denominator = (
            sum_of_productive_work_per_day + public_costs_per_day.labour_cost
        ) or 1
        # Payout factor
        payout_factor = numerator / denominator
        return Decimal(payout_factor)

    def _last_certificate_payout_was_today(self, plan: Plan) -> bool:
        if plan.last_certificate_payout is not None:
            return plan.last_certificate_payout.date() == self.datetime_service.today()
        return False

    def _plan_expires_today(self, plan: Plan) -> bool:
        if plan.expiration_date is not None:
            return plan.expiration_date.date() == self.datetime_service.today()
        return False

    def _credit_production_cost_to_planner(self, plan: Plan) -> None:
        self._create_transaction_from_social_accounting(
            plan, plan.planner.means_account, plan.production_costs.means_cost
        )
        self._create_transaction_from_social_accounting(
            plan, plan.planner.raw_material_account, plan.production_costs.resource_cost
        )
        self._create_transaction_from_social_accounting(
            plan, plan.planner.product_account, -plan.expected_sales_value
        )

    def _create_transaction_from_social_accounting(
        self, plan: Plan, account: Account, amount: Decimal
    ) -> None:
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=self.social_accounting.account,
            receiving_account=account,
            amount=round(amount, 2),
            purpose=f"Plan-Id: {plan.id}",
        )
