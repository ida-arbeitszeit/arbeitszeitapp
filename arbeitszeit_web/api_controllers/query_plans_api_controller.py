from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest


class QueryPlansApiController:
    def get_request(self) -> QueryPlansRequest:
        return QueryPlansRequest(
            query_string=None,
            filter_category=PlanFilter.by_plan_id,
            sorting_category=PlanSorting.by_activation,
        )
