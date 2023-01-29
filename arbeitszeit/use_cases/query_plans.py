from __future__ import annotations

import enum
import math
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import CompanyRepository, PlanRepository, PlanResult


class PlanFilter(enum.Enum):
    by_plan_id = enum.auto()
    by_product_name = enum.auto()


class PlanSorting(enum.Enum):
    by_activation = enum.auto()
    by_company_name = enum.auto()


@dataclass
class PlanQueryResponse:
    results: List[QueriedPlan]
    page: int
    num_pages: int


@dataclass
class QueriedPlan:
    plan_id: UUID
    company_name: str
    company_id: UUID
    product_name: str
    description: str
    price_per_unit: Decimal
    is_public_service: bool
    is_available: bool
    is_cooperating: bool
    activation_date: datetime


@dataclass
class QueryPlansRequest:
    query_string: Optional[str]
    filter_category: PlanFilter
    sorting_category: PlanSorting
    page: Optional[int] = None


@inject
@dataclass
class QueryPlans:
    plan_repository: PlanRepository
    company_repository: CompanyRepository
    price_calculator: PriceCalculator

    def __call__(self, request: QueryPlansRequest) -> PlanQueryResponse:
        query = request.query_string
        filter_by = request.filter_category
        sort_by = request.sorting_category

        LIMIT = 15
        current_page, offset, num_pages = self._get_pagination_attributes(
            limit=LIMIT, request=request
        )

        plans = self.plan_repository.get_plans().that_are_active()
        plans = self._apply_filter(plans, query, filter_by)
        plans = self._apply_sorting(plans, sort_by)
        # apply offset and limit
        plans = plans.offset(n=offset).limit(n=LIMIT)

        results = [self._plan_to_response_model(plan) for plan in plans]
        return PlanQueryResponse(
            results=results, page=current_page, num_pages=num_pages
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

    def _get_pagination_attributes(
        self, limit: int, request: QueryPlansRequest
    ) -> Tuple[int, int, int]:
        current_page = 1 if request.page is None else request.page
        offset = (current_page - 1) * limit
        num_pages = math.ceil(
            len(self.plan_repository.get_plans().that_are_active()) / limit
        )
        return (current_page, offset, num_pages)

    def _plan_to_response_model(self, plan: Plan) -> QueriedPlan:
        price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        assert plan.activation_date
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        return QueriedPlan(
            plan_id=plan.id,
            company_name=planner.name,
            company_id=plan.planner,
            product_name=plan.prd_name,
            description=plan.description,
            price_per_unit=price_per_unit,
            is_public_service=plan.is_public_service,
            is_available=plan.is_available,
            is_cooperating=bool(plan.cooperation),
            activation_date=plan.activation_date,
        )
