from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.repositories import (
    CompanyRepository,
    PayoutFactorRepository,
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
    payout_factor_service: PayoutFactorService
    payout_factor_repository: PayoutFactorRepository
    company_repository: CompanyRepository

    def __call__(self) -> None:
        """This function should be called at least once per day,
        preferably more often (e.g. every hour).
        """
        self._calculate_plan_expiration()
        payout_factor = self.payout_factor_service.calculate_payout_factor()
        self.payout_factor_service.store_payout_factor(payout_factor)
        plans = self.plan_repository.get_plans().that_are_active()
        for plan in plans:
            self._payout_work_certificates(plan, payout_factor)

    def _calculate_plan_expiration(self) -> None:
        for plan in self.plan_repository.get_plans().that_are_active():
            assert plan.is_active, "Plan is not active!"
            assert plan.activation_date, "Plan has no activation date!"

            self.plan_repository.set_active_days(
                plan, self._calculate_active_days(plan)
            )

            assert plan.active_days is not None
            if self._plan_is_expired(plan):
                self._handle_expired_plan(plan)

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
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=self.social_accounting.account.id,
            receiving_account=planner.work_account,
            amount_sent=round(amount, 2),
            amount_received=round(amount, 2),
            purpose=f"Plan-Id: {plan.id}",
        )
        self.plan_repository.increase_payout_count_by_one(plan)

    def _plan_is_expired(self, plan: Plan) -> bool:
        assert plan.expiration_date
        return self.datetime_service.now() > plan.expiration_date

    def _handle_expired_plan(self, plan: Plan) -> None:
        """Payout overdue wages, if there are any, applying the latest
        payout factor stored in repo. Delete plan's cooperation and
        coop request, if there is any. Set plan as expired.
        """
        assert plan.active_days
        while plan.payout_count < plan.active_days:
            payout_factor = self.payout_factor_repository.get_latest_payout_factor()
            if payout_factor is None:
                # overdue wages and no pf in repo should hardly ever happen
                # in this case best approximation is probably 1
                payout_factor_value = Decimal(1)
            else:
                payout_factor_value = payout_factor.value
            self._payout(plan, payout_factor_value)
        plans = self.plan_repository.get_plans().with_id(plan.id)
        plans.update().set_requested_cooperation(None).set_cooperation(
            None
        ).set_activation_status(is_active=False).set_expiration_status(
            is_expired=True
        ).perform()

    def _calculate_active_days(self, plan: Plan) -> int:
        """Returns the full days a plan has been active, not
        considering days exceeding it's timeframe.
        """
        assert plan.activation_date
        days_passed_since_activation = (
            self.datetime_service.now() - plan.activation_date
        ).days
        return min(plan.timeframe, days_passed_since_activation)
