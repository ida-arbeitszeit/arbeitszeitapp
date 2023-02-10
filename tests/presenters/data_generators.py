from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    PlanSorting,
    QueriedPlan,
    QueryPlansRequest,
)


class QueriedPlanGenerator:
    def get_plan(
        self,
        plan_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        is_cooperating: Optional[bool] = None,
        description: Optional[str] = None,
        activation_date: Optional[datetime] = None,
        price_per_unit: Optional[Decimal] = None,
    ) -> QueriedPlan:
        if plan_id is None:
            plan_id = uuid4()
        if company_id is None:
            company_id = uuid4()
        if is_cooperating is None:
            is_cooperating = False
        if description is None:
            description = "For eating\nNext paragraph\rThird one"
        if activation_date is None:
            activation_date = datetime.now()
        if price_per_unit is None:
            price_per_unit = Decimal(5)
        return QueriedPlan(
            plan_id=plan_id,
            company_name="Planner name",
            company_id=company_id,
            product_name="Bread",
            description=description,
            price_per_unit=price_per_unit,
            is_public_service=False,
            is_available=True,
            is_cooperating=is_cooperating,
            activation_date=activation_date,
        )

    def get_response(
        self,
        queried_plans: Optional[List[QueriedPlan]] = None,
        page: Optional[int] = None,
        num_pages: Optional[int] = None,
        total_results: Optional[int] = None,
        query_string: Optional[str] = None,
        requested_offset: int = 0,
        requested_limit: Optional[int] = None,
        requested_filter_category: PlanFilter = PlanFilter.by_product_name,
        requested_sorting_category: PlanSorting = PlanSorting.by_activation,
    ) -> PlanQueryResponse:
        if queried_plans is None:
            queried_plans = [self.get_plan() for _ in range(5)]
        if total_results is None:
            total_results = max(len(queried_plans), 100)
        return PlanQueryResponse(
            results=[plan for plan in queried_plans],
            total_results=total_results,
            request=QueryPlansRequest(
                offset=requested_offset,
                limit=requested_limit,
                query_string=query_string,
                filter_category=requested_filter_category,
                sorting_category=requested_sorting_category,
            ),
        )
