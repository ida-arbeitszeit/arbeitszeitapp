from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.repositories import (
    PlanCooperationRepository,
    PlanRepository,
    TransactionRepository,
)


@inject
@dataclass
class UpdatePlansAndPayout:
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting
    plan_cooperation_repository: PlanCooperationRepository
    payout_factor_service: PayoutFactorService

    def __call__(self) -> None:
        """
        This function should be called at least once per day,
        preferably more often (e.g. every hour).
        """
        payout_factor = self.payout_factor_service.calculate_payout_factor()
        self.payout_factor_service.store_payout_factor(payout_factor)
        self._calculate_plan_expiration(payout_factor)
        for plan in self.plan_repository.all_plans_approved_active_and_not_expired():
            self._payout_work_certificates(plan, payout_factor)

    def _calculate_plan_expiration(self, payout_factor: Decimal) -> None:
        for plan in self.plan_repository.get_active_plans():
            assert plan.is_active, "Plan is not active!"
            assert plan.activation_date, "Plan has no activation date!"

            self.plan_repository.set_active_days(
                plan, self._calculate_active_days(plan)
            )

            assert plan.active_days is not None
            if self._plan_is_expired(plan):
                self._handle_expired_plan(plan, payout_factor)

    def _payout_work_certificates(self, plan: Plan, payout_factor: Decimal) -> None:
        """
        Plans have an attribute "timeframe", that describe the length of the
        planning cycle in days.

        Work Certificates ("wages") have to be paid out daily
        and upfront (approx. at the time of day of the original plan activation) until
        the plan expires.

        The daily payout amount = current payout factor * total labour costs / plan timeframe.

        Thus, at any point in time, the number of payouts
        a company has received for a plan must be larger (by one)
        than the number of full days the plan has been active.
        (Only after expiration both numbers are equal.)

        If this requirement is not met, a payout is triggered to increase the number of payouts by one.
        """
        assert plan.active_days is not None
        while plan.payout_count <= plan.active_days:
            self._payout(plan, payout_factor)

    def _payout(self, plan: Plan, payout_factor: Decimal) -> None:
        amount = payout_factor * plan.production_costs.labour_cost / plan.timeframe
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=self.social_accounting.account,
            receiving_account=plan.planner.work_account,
            amount_sent=round(amount, 2),
            amount_received=round(amount, 2),
            purpose=f"Plan-Id: {plan.id}",
        )
        self.plan_repository.increase_payout_count_by_one(plan)

    def _plan_is_expired(self, plan: Plan) -> bool:
        assert plan.expiration_date
        return self.datetime_service.now() > plan.expiration_date

    def _handle_expired_plan(self, plan: Plan, payout_factor: Decimal) -> None:
        """
        payout overdue wages, if there are any
        delete plan's cooperation and coop request, if there is any
        set plan as expired
        """
        assert plan.active_days
        while plan.payout_count < plan.active_days:
            self._payout(plan, payout_factor)
        self._delete_cooperation_and_coop_request_from_plan(plan)
        self.plan_repository.set_plan_as_expired(plan)

    def _calculate_active_days(self, plan: Plan) -> int:
        """
        returns the full days a plan has been active,
        not considering days exceeding it's timeframe
        """
        assert plan.activation_date
        days_passed_since_activation = (
            self.datetime_service.now() - plan.activation_date
        ).days

        active_days = (
            plan.timeframe
            if (plan.timeframe < days_passed_since_activation)
            else days_passed_since_activation
        )
        return active_days

    def _delete_cooperation_and_coop_request_from_plan(self, plan: Plan) -> None:
        if plan.requested_cooperation:
            self.plan_cooperation_repository.set_requested_cooperation_to_none(plan.id)
        if plan.cooperation:
            self.plan_cooperation_repository.remove_plan_from_cooperation(plan.id)
