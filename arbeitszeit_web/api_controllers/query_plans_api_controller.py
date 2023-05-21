from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest
from arbeitszeit_web.api_controllers import query_parser
from arbeitszeit_web.api_controllers.expected_input import ExpectedInput
from arbeitszeit_web.request import Request

DEFAULT_OFFSET: int = 0
DEFAULT_LIMIT: int = 30


@dataclass
class QueryPlansApiController:
    @classmethod
    def create_expected_inputs(cls) -> List[ExpectedInput]:
        return [
            ExpectedInput(
                name="offset",
                type=str,
                description="The query offset.",
                default=DEFAULT_OFFSET,
            ),
            ExpectedInput(
                name="limit",
                type=str,
                description="The query limit.",
                default=DEFAULT_LIMIT,
            ),
        ]

    request: Request

    def create_request(self) -> QueryPlansRequest:
        offset = self._parse_offset(self.request)
        limit = self._parse_limit(self.request)
        return QueryPlansRequest(
            query_string=None,
            filter_category=PlanFilter.by_plan_id,
            sorting_category=PlanSorting.by_activation,
            offset=offset,
            limit=limit,
        )

    def _parse_offset(self, request: Request) -> int:
        offset_string = request.query_string().get("offset")
        if not offset_string:
            return DEFAULT_OFFSET
        offset = query_parser.string_to_non_negative_integer(offset_string)
        return offset

    def _parse_limit(self, request: Request) -> int:
        limit_string = request.query_string().get("limit")
        if not limit_string:
            return DEFAULT_LIMIT
        limit = query_parser.string_to_non_negative_integer(limit_string)
        return limit
