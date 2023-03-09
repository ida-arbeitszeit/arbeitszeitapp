from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.repositories import (
    CompanyRepository,
    DatabaseGateway,
    PlanRepository,
    TransactionRepository,
)


@dataclass
class UpdatePlansAndPayout:
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting
    payout_factor_service: PayoutFactorService
    company_repository: CompanyRepository
    database_gateway: DatabaseGateway

    def __call__(self) -> None:
        """This function should be called at least once per day,
        preferably more often (e.g. every hour).
        """
        self._calculate_plan_expiration()
        payout_factor = self.payout_factor_service.calculate_payout_factor()
        self.payout_factor_service.store_payout_factor(payout_factor)
        plans = self.plan_repository.get_plans().that_are_active()
        for plan in plans:
            payout_count = len(
                self.database_gateway.get_labour_certificates_payouts().for_plan(
                    plan.id
                )
            )
            self._payout_work_certificates(plan, payout_factor, payout_count)

    def _calculate_plan_expiration(self) -> None:
        payout_factor = self._get_latest_payout_factor()
        for plan in self.plan_repository.get_plans().that_are_active():
            assert plan.is_active, "Plan is not active!"
            assert plan.activation_date, "Plan has no activation date!"
            if self._plan_is_expired(plan):
                self._handle_expired_plan(plan, payout_factor)

    def _payout_work_certificates(
        self, plan: Plan, payout_factor: Decimal, payout_count: int
    ) -> None:
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
        active_days = plan.active_days(self.datetime_service.now())
        assert active_days is not None
        for _ in range(max(active_days - payout_count + 1, 0)):
            self._payout(plan, payout_factor)

    def _payout(self, plan: Plan, payout_factor: Decimal) -> None:
        amount = payout_factor * plan.production_costs.labour_cost / plan.timeframe
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        transaction = self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=self.social_accounting.account.id,
            receiving_account=planner.work_account,
            amount_sent=round(amount, 2),
            amount_received=round(amount, 2),
            purpose=f"Plan-Id: {plan.id}",
        )
        self.database_gateway.create_labour_certificates_payout(
            transaction=transaction.id, plan=plan.id
        )

    def _plan_is_expired(self, plan: Plan) -> bool:
        assert plan.expiration_date
        return self.datetime_service.now() > plan.expiration_date

    def _handle_expired_plan(self, plan: Plan, payout_factor: Decimal) -> None:
        """Payout overdue wages, if there are any, applying the latest
        payout factor stored in repo. Delete plan's cooperation and
        coop request, if there is any. Set plan as expired.
        """
        active_days = plan.active_days(self.datetime_service.now())
        assert active_days is not None
        payout_count = len(
            self.database_gateway.get_labour_certificates_payouts().for_plan(plan.id)
        )
        for _ in range(max(0, active_days - payout_count)):
            self._payout(plan, payout_factor)
        plans = self.plan_repository.get_plans().with_id(plan.id)
        plans.update().set_requested_cooperation(None).set_cooperation(
            None
        ).set_activation_status(is_active=False).set_expiration_status(
            is_expired=True
        ).perform()

    def _get_latest_payout_factor(self) -> Decimal:
        factor = (
            self.database_gateway.get_payout_factors()
            .ordered_by_calculation_date(descending=True)
            .first()
        )
        if factor is None:
            return Decimal(1)
        else:
            return factor.value
