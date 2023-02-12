from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonDict,
    JsonString,
    JsonValue,
)


class ActivePlansPresenter:
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
                )
            ),
            schema_name="PlanList",
        )
