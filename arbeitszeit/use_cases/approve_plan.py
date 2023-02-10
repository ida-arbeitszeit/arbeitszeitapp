from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.repositories import (
    CompanyRepository,
    PlanRepository,
    TransactionRepository,
)


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
    company_repository: CompanyRepository

    def approve_plan(self, request: Request) -> Response:
        matching_plans = self.plan_repository.get_plans().with_id(request.plan)
        plan = matching_plans.first()
        assert plan
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        if plan.is_approved:
            return self.Response(is_approved=False)
        matching_plans.update().set_approval_date(
            self.datetime_service.now()
        ).set_approval_reason("approved").set_activation_timestamp(
            self.datetime_service.now()
        ).set_activation_status(
            is_active=True
        ).perform()
        self._create_transaction_from_social_accounting(
            plan, planner.means_account, plan.production_costs.means_cost
        )
        self._create_transaction_from_social_accounting(
            plan, planner.raw_material_account, plan.production_costs.resource_cost
        )
        self._create_transaction_from_social_accounting(
            plan, planner.product_account, -plan.expected_sales_value
        )
        return self.Response()

    def _create_transaction_from_social_accounting(
        self, plan: Plan, account: UUID, amount: Decimal
    ) -> None:
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=self.social_accounting.account.id,
            receiving_account=account,
            amount_sent=round(amount, 2),
            amount_received=round(amount, 2),
            purpose=f"Plan-Id: {plan.id}",
        )
