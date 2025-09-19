from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.interactors.query_plans import PlanQueryResponse, QueriedPlan
from arbeitszeit_web.api.presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonList,
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
                results=JsonList(
                    elements=JsonObject(
                        members=dict(
                            plan_id=JsonString(),
                            company_name=JsonString(),
                            company_id=JsonString(),
                            product_name=JsonString(),
                            description=JsonString(),
                            price_per_unit=JsonDecimal(),
                            is_public_service=JsonBoolean(),
                            is_cooperating=JsonBoolean(),
                            approval_date=JsonDatetime(),
                        ),
                        name="Plan",
                    )
                ),
                total_results=JsonInteger(),
                offset=JsonInteger(),
                limit=JsonInteger(),
            ),
            name="PlanList",
        )

    def create_view_model(self, interactor_response: PlanQueryResponse) -> ViewModel:
        return self.ViewModel(
            results=interactor_response.results,
            total_results=interactor_response.total_results,
            offset=interactor_response.request.offset,
            limit=interactor_response.request.limit,
        )
