from dataclasses import dataclass

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest
from arbeitszeit_web.api.controllers import query_parser
from arbeitszeit_web.api.controllers.parameters import QueryParameter
from arbeitszeit_web.request import Request

DEFAULT_OFFSET: int = 0
DEFAULT_LIMIT: int = 30


active_plans_expected_inputs = [
    QueryParameter(
        name="offset",
        type=int,
        description="The query offset.",
        default=DEFAULT_OFFSET,
    ),
    QueryParameter(
        name="limit",
        type=int,
        description="The query limit.",
        default=DEFAULT_LIMIT,
    ),
]


@dataclass
class QueryPlansApiController:
    def create_request(self, request: Request) -> QueryPlansRequest:
        offset = self._parse_offset(request)
        limit = self._parse_limit(request)
        return QueryPlansRequest(
            query_string=None,
            filter_category=PlanFilter.by_plan_id,
            sorting_category=PlanSorting.by_activation,
            include_expired_plans=False,
            offset=offset,
            limit=limit,
        )

    def _parse_offset(self, request: Request) -> int:
        offset_string = request.query_string().get_last_value("offset")
        if not offset_string:
            return DEFAULT_OFFSET
        offset = query_parser.string_to_non_negative_integer(offset_string)
        return offset

    def _parse_limit(self, request: Request) -> int:
        limit_string = request.query_string().get_last_value("limit")
        if not limit_string:
            return DEFAULT_LIMIT
        limit = query_parser.string_to_non_negative_integer(limit_string)
        return limit
