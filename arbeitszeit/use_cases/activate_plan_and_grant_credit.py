from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Account, Plan, SocialAccounting
from arbeitszeit.repositories import PlanRepository, TransactionRepository


@inject
@dataclass
class ActivatePlanAndGrantCredit:
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting

    def __call__(self, plan_id: UUID) -> None:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        assert plan, "Plan does not exist"
        assert plan.approved, "Plan has not been approved"
        self.plan_repository.activate_plan(plan, self.datetime_service.now())
        self._credit_production_cost_to_planner(plan)

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
            amount_sent=round(amount, 2),
            amount_received=round(amount, 2),
            purpose=f"Plan-Id: {plan.id}",
        )
