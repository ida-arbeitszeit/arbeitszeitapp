from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Account, Plan, PlanDraft, SocialAccounting
from arbeitszeit.repositories import (
    PlanDraftRepository,
    PlanRepository,
    TransactionRepository,
)


@inject
@dataclass
class SelfApprovePlan:
    @dataclass
    class Request:
        draft_id: UUID

    @dataclass
    class Response:
        is_approved: bool
        reason: str
        new_plan_id: UUID

    datetime_service: DatetimeService
    plan_repository: PlanRepository
    draft_repository: PlanDraftRepository
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting

    def __call__(self, request: Request) -> Response:
        draft = self.draft_repository.get_by_id(request.draft_id)
        assert draft is not None
        new_plan = self.approve_plan_and_delete_draft(draft)
        assert new_plan.approval_reason
        self.plan_repository.activate_plan(new_plan, self.datetime_service.now())
        self._credit_production_cost_to_planner(new_plan)

        return self.Response(
            is_approved=True, reason=new_plan.approval_reason, new_plan_id=new_plan.id
        )

    def approve_plan_and_delete_draft(self, draft: PlanDraft) -> Plan:
        new_plan = self.plan_repository.set_plan_approval_date(
            draft, self.get_approval_date()
        )
        self.draft_repository.delete_draft(draft.id)
        return new_plan

    def get_approval_date(self) -> datetime:
        return self.datetime_service.now()

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
