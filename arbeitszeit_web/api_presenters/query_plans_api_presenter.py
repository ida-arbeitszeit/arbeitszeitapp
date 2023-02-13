from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.query_plans import PlanQueryResponse, QueriedPlan
from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonDict,
    JsonInteger,
    JsonString,
    JsonValue,
)


class QueryPlansApiPresenter:
    @dataclass
    class ViewModel:
        results: List[QueriedPlan]
        total_results: int
        offset: int
        limit: int

    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonDict(
            members=dict(
                results=JsonDict(
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
                    schema_name="Plan",
                    as_list=True,
                ),
                total_results=JsonInteger(),
                offset=JsonInteger(),
                limit=JsonInteger(),
            ),
            schema_name="PlanList",
        )

    def create_view_model(self, use_case_response: PlanQueryResponse) -> ViewModel:
        offset = use_case_response.request.offset
        assert offset is not None
        limit = use_case_response.request.limit
        assert limit is not None
        return self.ViewModel(
            results=use_case_response.results,
            total_results=use_case_response.total_results,
            offset=offset,
            limit=limit,
        )
