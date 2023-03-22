from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.use_cases.query_companies import CompanyFilter, QueryCompaniesRequest
from arbeitszeit_web.api_controllers import query_parser
from arbeitszeit_web.api_controllers.expected_input import ExpectedInput
from arbeitszeit_web.request import Request

DEFAULT_OFFSET: int = 0
DEFAULT_LIMIT: int = 30


@dataclass
class QueryCompaniesRequestImpl(QueryCompaniesRequest):
    query: Optional[str]
    filter_category: CompanyFilter
    offset: int
    limit: int

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> CompanyFilter:
        return self.filter_category

    def get_offset(self) -> Optional[int]:
        return self.offset

    def get_limit(self) -> Optional[int]:
        return self.limit


class QueryCompaniesApiController:
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

    def create_request(self, request: Request) -> QueryCompaniesRequest:
        offset = self._parse_offset(request)
        limit = self._parse_limit(request)
        return QueryCompaniesRequestImpl(
            query=None,
            filter_category=CompanyFilter.by_name,
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
