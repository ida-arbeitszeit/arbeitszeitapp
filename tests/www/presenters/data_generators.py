from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from arbeitszeit.plan_details import PlanDetails
from arbeitszeit.use_cases.query_companies import (
    CompanyFilter,
    CompanyQueryResponse,
    QueriedCompany,
    QueryCompaniesRequest,
)
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
        rejection_date: Optional[datetime] = None,
        price_per_unit: Optional[Decimal] = None,
        labour_cost_per_unit: Optional[Decimal] = None,
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
        if rejection_date is None:
            rejection_date = datetime.now()
        if price_per_unit is None:
            price_per_unit = Decimal(5)
        if labour_cost_per_unit is None:
            labour_cost_per_unit = Decimal(1)
        return QueriedPlan(
            plan_id=plan_id,
            company_name="Planner name",
            company_id=company_id,
            product_name="Bread",
            description=description,
            price_per_unit=price_per_unit,
            labour_cost_per_unit=labour_cost_per_unit,
            is_public_service=False,
            is_cooperating=is_cooperating,
            activation_date=activation_date,
        )

    def get_response(
        self,
        queried_plans: Optional[List[QueriedPlan]] = None,
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


class QueriedCompanyGenerator:
    def get_company(self, name: Optional[str] = None) -> QueriedCompany:
        if name is None:
            name = "Some Company Name"
        return QueriedCompany(
            company_id=uuid4(), company_email="some.mail@cp.org", company_name=name
        )

    def get_response(
        self,
        queried_companies: Optional[List[QueriedCompany]] = None,
        total_results: Optional[int] = None,
        query_string: Optional[str] = None,
        requested_offset: int = 0,
        requested_limit: Optional[int] = None,
        requested_filter_category: CompanyFilter = CompanyFilter.by_name,
    ) -> CompanyQueryResponse:
        if queried_companies is None:
            queried_companies = [self.get_company() for _ in range(5)]
        if total_results is None:
            total_results = max(len(queried_companies), 100)
        return CompanyQueryResponse(
            results=[company for company in queried_companies],
            total_results=total_results,
            request=QueryCompaniesRequest(
                offset=requested_offset,
                limit=requested_limit,
                query_string=query_string,
                filter_category=requested_filter_category,
            ),
        )


class PlanDetailsGenerator:
    def create_plan_details(
        self,
        plan_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        planner_id: Optional[UUID] = None,
        planner_name: Optional[str] = None,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        active_days: Optional[int] = None,
        timeframe: Optional[int] = None,
        production_unit: Optional[str] = None,
        amount: Optional[int] = None,
        means_cost: Optional[Decimal] = None,
        resources_cost: Optional[Decimal] = None,
        labour_cost: Optional[Decimal] = None,
        is_public_service: Optional[bool] = None,
        labour_cost_per_unit: Optional[Decimal] = None,
        price_per_unit: Optional[Decimal] = None,
        is_cooperating: Optional[bool] = None,
        cooperation: Optional[UUID] = None,
        creation_date: Optional[datetime] = None,
        approval_date: Optional[datetime] = None,
        expiration_date: Optional[datetime] = None,
    ) -> PlanDetails:
        if plan_id is None:
            plan_id = uuid4()
        if is_active is None:
            is_active = True
        if planner_id is None:
            planner_id = uuid4()
        if planner_name is None:
            planner_name = "planner name"
        if product_name is None:
            product_name = "product name"
        if description is None:
            description = "test description"
        if active_days is None:
            active_days = 5
        if timeframe is None:
            timeframe = 7
        if production_unit is None:
            production_unit = "Piece"
        if amount is None:
            amount = 100
        if means_cost is None:
            means_cost = Decimal(1)
        if resources_cost is None:
            resources_cost = Decimal(2)
        if labour_cost is None:
            labour_cost = Decimal(3)
        if is_public_service is None:
            is_public_service = False
        if labour_cost_per_unit is None:
            labour_cost_per_unit = Decimal("0.875")
        if price_per_unit is None:
            price_per_unit = Decimal("0.061")
        if is_cooperating is None:
            is_cooperating = False
        if creation_date is None:
            creation_date = datetime(2023, 5, 1)
        assert isinstance(cooperation, UUID) or (cooperation is None)
        return PlanDetails(
            plan_id=plan_id,
            is_active=is_active,
            planner_id=planner_id,
            planner_name=planner_name,
            product_name=product_name,
            description=description,
            active_days=active_days,
            timeframe=timeframe,
            production_unit=production_unit,
            amount=amount,
            means_cost=means_cost,
            resources_cost=resources_cost,
            labour_cost=labour_cost,
            is_public_service=is_public_service,
            price_per_unit=price_per_unit,
            labour_cost_per_unit=labour_cost_per_unit,
            is_cooperating=is_cooperating,
            cooperation=cooperation,
            creation_date=creation_date,
            approval_date=approval_date,
            expiration_date=expiration_date,
        )
