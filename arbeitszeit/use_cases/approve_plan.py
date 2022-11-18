from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Account, Plan, SocialAccounting
from arbeitszeit.repositories import PlanRepository, TransactionRepository


@inject
@dataclass
class ApprovePlanUseCase:
    @dataclass
    class Request:
        plan: UUID

    @dataclass
    class Response:
        is_approved: bool = True

    plan_repository: PlanRepository
    datetime_service: DatetimeService
    social_accounting: SocialAccounting
    transaction_repository: TransactionRepository

    def approve_plan(self, request: Request) -> Response:
        plan = self.plan_repository.get_all_plans().with_id(request.plan).first()
        assert plan
        if plan.is_approved:
            return self.Response(is_approved=False)
        self.plan_repository.set_plan_approval_date(
            plan=request.plan, approval_timestamp=self.datetime_service.now()
        )
        self.plan_repository.activate_plan(
            plan=plan, activation_date=self.datetime_service.now()
        )
        self._create_transaction_from_social_accounting(
            plan, plan.planner.means_account, plan.production_costs.means_cost
        )
        self._create_transaction_from_social_accounting(
            plan, plan.planner.raw_material_account, plan.production_costs.resource_cost
        )
        self._create_transaction_from_social_accounting(
            plan, plan.planner.product_account, -plan.expected_sales_value
        )
        return self.Response()

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
