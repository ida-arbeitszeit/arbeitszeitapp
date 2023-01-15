from arbeitszeit_web.api_presenters.interfaces import JsonDict, JsonString, JsonValue


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
                    ),
                    schema_name="Plan",
                )
            ),
            schema_name="PlanList",
            as_list=True,
        )
