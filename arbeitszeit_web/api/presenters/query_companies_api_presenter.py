from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.interactors.query_companies import CompanyQueryResponse, QueriedCompany
from arbeitszeit_web.api.presenters.interfaces import (
    JsonInteger,
    JsonList,
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
                results=JsonList(
                    elements=JsonObject(
                        members=dict(
                            company_id=JsonString(),
                            company_email=JsonString(),
                            company_name=JsonString(),
                        ),
                        name="Company",
                    )
                ),
                total_results=JsonInteger(),
                offset=JsonInteger(),
                limit=JsonInteger(),
            ),
            name="CompanyList",
        )

    def create_view_model(self, interactor_response: CompanyQueryResponse) -> ViewModel:
        return self.ViewModel(
            results=interactor_response.results,
            total_results=interactor_response.total_results,
            offset=interactor_response.request.offset,
            limit=interactor_response.request.limit,
        )
