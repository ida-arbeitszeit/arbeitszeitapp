from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.use_cases.query_companies import CompanyQueryResponse, QueriedCompany
from arbeitszeit_web.api.presenters.interfaces import (
    JsonInteger,
    JsonObject,
    JsonString,
    JsonValue,
)


class QueryCompaniesApiPresenter:
    @dataclass
    class ViewModel:
        results: List[QueriedCompany]
        total_results: int
        offset: Optional[int]
        limit: Optional[int]

    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonObject(
            members=dict(
                results=JsonObject(
                    members=dict(
                        company_id=JsonString(),
                        company_email=JsonString(),
                        company_name=JsonString(),
                    ),
                    name="Company",
                    as_list=True,
                ),
                total_results=JsonInteger(),
                offset=JsonInteger(),
                limit=JsonInteger(),
            ),
            name="CompanyList",
        )

    def create_view_model(self, use_case_response: CompanyQueryResponse) -> ViewModel:
        return self.ViewModel(
            results=use_case_response.results,
            total_results=use_case_response.total_results,
            offset=use_case_response.request.offset,
            limit=use_case_response.request.limit,
        )
