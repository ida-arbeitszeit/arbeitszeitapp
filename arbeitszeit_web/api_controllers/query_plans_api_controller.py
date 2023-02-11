from dataclasses import dataclass
from typing import List, Type, Union

from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting, QueryPlansRequest
from arbeitszeit_web.request import Request

DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 30


class NotAnIntegerError(ValueError):
    pass


class NegativeNumberError(ValueError):
    pass


@dataclass
class ExpectedInput:
    name: str
    type: Type
    description: str
    default: Union[None, str, int, bool]


class QueryPlansApiController:
    @property
    def expected_inputs(self) -> List[ExpectedInput]:
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

    def get_request(self, request: Request) -> QueryPlansRequest:
        offset = self._parse_offset(request)
        limit = self._parse_limit(request)
        return QueryPlansRequest(
            query_string=None,
            filter_category=PlanFilter.by_plan_id,
            sorting_category=PlanSorting.by_activation,
            offset=offset,
            limit=limit,
        )

    def _parse_offset(self, request: Request) -> int:
        offset: int = DEFAULT_OFFSET
        value = request.query_string().get("offset")
        if not value:
            return offset
        try:
            offset = int(value)
        except ValueError:
            raise NotAnIntegerError()
        else:
            if offset < 0:
                raise NegativeNumberError()
        return offset

    def _parse_limit(self, request: Request) -> int:
        limit: int = DEFAULT_LIMIT
        value = request.query_string().get("limit")
        if not value:
            return limit
        try:
            limit = int(value)
        except ValueError:
            raise NotAnIntegerError()
        else:
            if limit < 0:
                raise NegativeNumberError()
        return limit
