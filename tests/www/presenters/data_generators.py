from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from arbeitszeit.interactors.query_companies import (
    CompanyFilter,
    CompanyQueryResponse,
    QueriedCompany,
    QueryCompaniesRequest,
)
from arbeitszeit.interactors.query_plans import (
    PlanFilter,
    PlanQueryResponse,
    PlanSorting,
    QueriedPlan,
    QueryPlansRequest,
)
from arbeitszeit.services.plan_details import PlanDetails
from tests.datetime_service import datetime_utc


class QueriedPlanGenerator:
    def get_plan(
        self,
        plan_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        is_cooperating: bool = False,
        description: str = "For eating\nNext paragraph\rThird one",
        approval_date: Optional[datetime] = None,
        rejection_date: Optional[datetime] = None,
        price_per_unit: Decimal = Decimal(5),
        labour_cost_per_unit: Decimal = Decimal(1),
        is_expired: bool = False,
    ) -> QueriedPlan:
        if plan_id is None:
            plan_id = uuid4()
        if company_id is None:
            company_id = uuid4()
        if approval_date is None:
            approval_date = datetime.min
        if rejection_date is None:
            rejection_date = datetime.min
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
            approval_date=approval_date,
            is_expired=is_expired,
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
                include_expired_plans=False,
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
        is_active: bool = True,
        planner_id: Optional[UUID] = None,
        planner_name: str = "planner name",
        product_name: str = "product name",
        description: str = "test description",
        active_days: int = 5,
        timeframe: int = 7,
        production_unit: str = "Piece",
        amount: int = 100,
        means_cost: Decimal = Decimal(1),
        resources_cost: Decimal = Decimal(2),
        labour_cost: Decimal = Decimal(3),
        is_public_service: bool = False,
        labour_cost_per_unit: Decimal = Decimal(0.875),
        price_per_unit: Decimal = Decimal(0.061),
        is_cooperating: bool = False,
        cooperation: Optional[UUID] = None,
        creation_date: datetime = datetime_utc(2023, 5, 1),
        approval_date: Optional[datetime] = None,
        expiration_date: Optional[datetime] = None,
    ) -> PlanDetails:
        if plan_id is None:
            plan_id = uuid4()
        if planner_id is None:
            planner_id = uuid4()
        if is_cooperating is None:
            is_cooperating = False
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
