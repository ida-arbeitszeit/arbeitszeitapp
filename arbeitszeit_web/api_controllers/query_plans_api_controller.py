from typing import Optional

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest


class QueryPlansRequestImpl(QueryPlansRequest):
    def get_query_string(self) -> Optional[str]:
        return None

    def get_filter_category(self) -> PlanFilter:
        return PlanFilter.by_plan_id

    def get_sorting_category(self) -> PlanSorting:
        return PlanSorting.by_activation


class QueryPlansApiController:
    def get_request(self) -> QueryPlansRequest:
        return QueryPlansRequestImpl()
