from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.use_cases.query_companies import CompanyQueryResponse, QueriedCompany
from arbeitszeit_web.api_presenters.interfaces import (
    JsonDict,
    JsonInteger,
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
        return JsonDict(
            members=dict(
                results=JsonDict(
                    members=dict(
                        company_id=JsonString(),
                        company_email=JsonString(),
                        company_name=JsonString(),
                    ),
                    schema_name="Company",
                    as_list=True,
                ),
                total_results=JsonInteger(),
                offset=JsonInteger(),
                limit=JsonInteger(),
            ),
            schema_name="CompanyList",
        )

    def create_view_model(self, use_case_response: CompanyQueryResponse) -> ViewModel:
        return self.ViewModel(
            results=use_case_response.results,
            total_results=use_case_response.total_results,
            offset=use_case_response.request.get_offset(),
            limit=use_case_response.request.get_limit(),
        )
