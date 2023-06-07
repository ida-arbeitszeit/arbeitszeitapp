from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, SocialAccounting
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ApprovePlanUseCase:
    @dataclass
    class Request:
        plan: UUID

    @dataclass
    class Response:
        is_approved: bool = True

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    social_accounting: SocialAccounting

    def approve_plan(self, request: Request) -> Response:
        now = self.datetime_service.now()
        matching_plans = self.database_gateway.get_plans().with_id(request.plan)
        plan = matching_plans.first()
        assert plan
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        if plan.is_approved:
            return self.Response(is_approved=False)
        matching_plans.update().set_approval_date(now).set_activation_timestamp(
            now
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
        self.database_gateway.create_transaction(
            date=self.datetime_service.now(),
            sending_account=self.social_accounting.account,
            receiving_account=account,
            amount_sent=round(amount, 2),
            amount_received=round(amount, 2),
            plan=plan.id,
        )
