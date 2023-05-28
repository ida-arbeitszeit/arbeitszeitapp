from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.use_cases.query_plans import PlanQueryResponse, QueriedPlan
from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
    JsonValue,
)


class QueryPlansApiPresenter:
    @dataclass
    class ViewModel:
        results: List[QueriedPlan]
        total_results: int
        offset: Optional[int]
        limit: Optional[int]

    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonObject(
            members=dict(
                results=JsonObject(
                    members=dict(
                        plan_id=JsonString(),
                        company_name=JsonString(),
                        company_id=JsonString(),
                        product_name=JsonString(),
                        description=JsonString(),
                        price_per_unit=JsonDecimal(),
                        is_public_service=JsonBoolean(),
                        is_available=JsonBoolean(),
                        is_cooperating=JsonBoolean(),
                        activation_date=JsonDatetime(),
                    ),
                    name="Plan",
                    as_list=True,
                ),
                total_results=JsonInteger(),
                offset=JsonInteger(),
                limit=JsonInteger(),
            ),
            name="PlanList",
        )

    def create_view_model(self, use_case_response: PlanQueryResponse) -> ViewModel:
        return self.ViewModel(
            results=use_case_response.results,
            total_results=use_case_response.total_results,
            offset=use_case_response.request.offset,
            limit=use_case_response.request.limit,
        )
