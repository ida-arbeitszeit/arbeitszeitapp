from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, PlanDraft
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import DatabaseGateway, PlanDraftRepository


@dataclass
class ShowMyPlansRequest:
    company_id: UUID


@dataclass
class PlanInfo:
    id: UUID
    prd_name: str
    price_per_unit: Decimal
    is_public_service: bool
    plan_creation_date: datetime
    activation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    is_available: bool
    is_cooperating: bool
    cooperation: Optional[UUID]


@dataclass
class ShowMyPlansResponse:
    count_all_plans: int
    non_active_plans: List[PlanInfo]
    active_plans: List[PlanInfo]
    expired_plans: List[PlanInfo]
    drafts: List[PlanInfo]


@dataclass
class ShowMyPlansUseCase:
    database_gateway: DatabaseGateway
    draft_repository: PlanDraftRepository
    price_calculator: PriceCalculator
    datetime_service: DatetimeService

    def show_company_plans(self, request: ShowMyPlansRequest) -> ShowMyPlansResponse:
        now = self.datetime_service.now()
        all_plans_of_company = list(
            self.database_gateway.get_plans()
            .planned_by(request.company_id)
            .ordered_by_creation_date(ascending=False)
            .that_are_not_hidden()
        )
        drafts = list(
            map(
                self._create_plan_info_from_draft,
                self.draft_repository.get_plan_drafts().planned_by(request.company_id),
            )
        )
        drafts.sort(key=lambda x: x.plan_creation_date, reverse=True)
        count_all_plans = len(all_plans_of_company) + len(drafts)
        non_active_plans = [
            self._create_plan_info_from_plan(plan)
            for plan in all_plans_of_company
            if (
                not plan.is_approved
                and not plan.is_active_as_of(now)
                and not plan.is_expired_as_of(now)
            )
        ]
        active_plans = [
            self._create_plan_info_from_plan(plan)
            for plan in all_plans_of_company
            if (
                plan.is_approved
                and plan.is_active_as_of(now)
                and not plan.is_expired_as_of(now)
            )
        ]
        expired_plans = [
            self._create_plan_info_from_plan(plan)
            for plan in all_plans_of_company
            if plan.is_expired_as_of(now)
        ]
        return ShowMyPlansResponse(
            count_all_plans=count_all_plans,
            non_active_plans=non_active_plans,
            active_plans=active_plans,
            expired_plans=expired_plans,
            drafts=drafts,
        )

    def _create_plan_info_from_plan(self, plan: Plan) -> PlanInfo:
        return PlanInfo(
            id=plan.id,
            prd_name=plan.prd_name,
            price_per_unit=self.price_calculator.calculate_cooperative_price(plan),
            is_public_service=plan.is_public_service,
            plan_creation_date=plan.plan_creation_date,
            activation_date=plan.activation_date,
            expiration_date=plan.expiration_date,
            is_available=plan.is_available,
            is_cooperating=bool(plan.cooperation),
            cooperation=plan.cooperation,
        )

    def _create_plan_info_from_draft(self, draft: PlanDraft) -> PlanInfo:
        return PlanInfo(
            id=draft.id,
            prd_name=draft.product_name,
            price_per_unit=draft.production_costs.total_cost() / draft.amount_produced,
            is_public_service=draft.is_public_service,
            plan_creation_date=draft.creation_date,
            activation_date=None,
            expiration_date=None,
            is_available=False,
            is_cooperating=False,
            cooperation=None,
        )
