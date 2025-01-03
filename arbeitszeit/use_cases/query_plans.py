from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import DatabaseGateway, PlanResult


class PlanFilter(enum.Enum):
    by_plan_id = enum.auto()
    by_product_name = enum.auto()


class PlanSorting(enum.Enum):
    by_activation = enum.auto()
    by_company_name = enum.auto()


@dataclass
class PlanQueryResponse:
    results: List[QueriedPlan]
    total_results: int
    request: QueryPlansRequest


@dataclass
class QueriedPlan:
    plan_id: UUID
    company_name: str
    company_id: UUID
    product_name: str
    description: str
    price_per_unit: Decimal
    labour_cost_per_unit: Decimal
    is_public_service: bool
    is_cooperating: bool
    activation_date: datetime
    is_expired: bool


@dataclass
class QueryPlansRequest:
    query_string: Optional[str]
    filter_category: PlanFilter
    sorting_category: PlanSorting
    include_expired_plans: bool
    offset: Optional[int] = None
    limit: Optional[int] = None


@dataclass
class QueryPlans:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator

    def __call__(self, request: QueryPlansRequest) -> PlanQueryResponse:
        now = self.datetime_service.now()
        plans = self.database_gateway.get_plans().that_were_activated_before(now)
        if not request.include_expired_plans:
            plans = plans.that_will_expire_after(now)
        plans = self._apply_filter(plans, request.query_string, request.filter_category)
        total_results = len(plans)
        plans = self._apply_sorting(plans, request.sorting_category)
        planning_info = plans.joined_with_planner_and_cooperation()
        if request.offset is not None:
            planning_info = planning_info.offset(n=request.offset)
        if request.limit is not None:
            planning_info = planning_info.limit(n=request.limit)
        results = [
            self._plan_to_response_model(plan, planner, cooperation)
            for plan, planner, cooperation in planning_info
        ]
        return PlanQueryResponse(
            results=results, total_results=total_results, request=request
        )

    def _apply_filter(
        self, plans: PlanResult, query: Optional[str], filter_by: PlanFilter
    ) -> PlanResult:
        if query is None:
            pass
        elif filter_by == PlanFilter.by_plan_id:
            plans = plans.with_id_containing(query)
        else:
            plans = plans.with_product_name_containing(query)
        return plans

    def _apply_sorting(self, plans: PlanResult, sort_by: PlanSorting) -> PlanResult:
        if sort_by == PlanSorting.by_company_name:
            plans = plans.ordered_by_planner_name()
        else:
            plans = plans.ordered_by_activation_date(ascending=False)
        return plans

    def _plan_to_response_model(
        self,
        plan: records.Plan,
        planner: records.Company,
        cooperation: Optional[records.Cooperation],
    ) -> QueriedPlan:
        price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        assert plan.activation_date
        return QueriedPlan(
            plan_id=plan.id,
            company_name=planner.name,
            company_id=plan.planner,
            product_name=plan.prd_name,
            description=plan.description,
            price_per_unit=price_per_unit,
            labour_cost_per_unit=plan.cost_per_unit(),
            is_public_service=plan.is_public_service,
            is_cooperating=bool(cooperation),
            activation_date=plan.activation_date,
            is_expired=plan.is_expired_as_of(self.datetime_service.now()),
        )
