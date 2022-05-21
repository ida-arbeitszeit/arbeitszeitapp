from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import PlanCooperationRepository, PlanRepository


class PlanFilter(enum.Enum):
    by_plan_id = enum.auto()
    by_product_name = enum.auto()


@dataclass
class PlanQueryResponse:
    results: List[QueriedPlan]


@dataclass
class QueriedPlan:
    plan_id: UUID
    company_name: str
    company_id: UUID
    product_name: str
    description: str
    price_per_unit: Decimal
    is_public_service: bool
    expiration_relative: Optional[int]
    is_available: bool
    is_cooperating: bool
    cooperation: Optional[UUID]


class QueryPlansRequest(ABC):
    @abstractmethod
    def get_query_string(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_filter_category(self) -> PlanFilter:
        pass


@inject
@dataclass
class QueryPlans:
    plan_repository: PlanRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, request: QueryPlansRequest) -> PlanQueryResponse:
        query = request.get_query_string()
        filter_by = request.get_filter_category()
        if query is None:
            found_plans = self.plan_repository.get_active_plans()
        elif filter_by == PlanFilter.by_plan_id:
            found_plans = self.plan_repository.query_active_plans_by_plan_id(query)
        else:
            found_plans = self.plan_repository.query_active_plans_by_product_name(query)
        results = [self._plan_to_response_model(plan) for plan in found_plans]
        return PlanQueryResponse(
            results=results,
        )

    def _plan_to_response_model(self, plan: Plan) -> QueriedPlan:
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        return QueriedPlan(
            plan_id=plan.id,
            company_name=plan.planner.name,
            company_id=plan.planner.id,
            product_name=plan.prd_name,
            description=plan.description,
            price_per_unit=price_per_unit,
            is_public_service=plan.is_public_service,
            expiration_relative=plan.expiration_relative,
            is_available=plan.is_available,
            is_cooperating=bool(plan.cooperation),
            cooperation=plan.cooperation,
        )
