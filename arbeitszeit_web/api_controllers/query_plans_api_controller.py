from typing import List

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest
from arbeitszeit_web.api_controllers.errors import (
    NegativeNumberError,
    NotAnIntegerError,
)
from arbeitszeit_web.api_controllers.expected_input import ExpectedInput
from arbeitszeit_web.request import Request

DEFAULT_OFFSET: int = 0
DEFAULT_LIMIT: int = 30


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

    def create_request(self, request: Request) -> QueryPlansRequest:
        offset = self._parse_offset(request)
        limit = self._parse_limit(request)
        return QueryPlansRequest(
            query_string=None,
            filter_category=PlanFilter.by_plan_id,
            sorting_category=PlanSorting.by_activation,
            offset=offset,
            limit=limit,
        )

    def _string_to_non_negative_integer(self, string: str) -> int:
        try:
            integer = int(string)
        except ValueError:
            raise NotAnIntegerError()
        else:
            if integer < 0:
                raise NegativeNumberError()
        return integer

    def _parse_offset(self, request: Request) -> int:
        offset_string = request.query_string().get("offset")
        if not offset_string:
            return DEFAULT_OFFSET
        offset = self._string_to_non_negative_integer(offset_string)
        return offset

    def _parse_limit(self, request: Request) -> int:
        limit_string = request.query_string().get("limit")
        if not limit_string:
            return DEFAULT_LIMIT
        limit = self._string_to_non_negative_integer(limit_string)
        return limit
