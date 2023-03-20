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
        now = self.datetime_service.now()
        payout_factor = self.payout_factor_service.calculate_payout_factor()
        self.payout_factor_service.store_payout_factor(payout_factor)
        plans = self.plan_repository.get_plans().where_payout_counts_are_less_then_active_days(
            now
        )
        for plan in plans:
            payout_count = len(
                self.database_gateway.get_labour_certificates_payouts().for_plan(
                    plan.id
                )
            )
            self._payout_work_certificates(plan, payout_factor, payout_count)

    def _payout_work_certificates(
        self, plan: Plan, payout_factor: Decimal, payout_count: int
    ) -> None:
        """Work Certificates ("wages") are paid out daily until the
        plan expires.
        """
        active_days = plan.active_days(self.datetime_service.now())
        assert active_days is not None
        for _ in range(max(active_days - payout_count, 0)):
            self._payout(plan, payout_factor)
        if self._plan_is_expired(plan):
            self._handle_expired_plan(plan, payout_factor)

    def _payout(self, plan: Plan, payout_factor: Decimal) -> None:
        """The daily payout amount = current payout factor * total
        labour costs / plan timeframe.
        """
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
        plans.update().set_requested_cooperation(None).set_cooperation(None).perform()

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
