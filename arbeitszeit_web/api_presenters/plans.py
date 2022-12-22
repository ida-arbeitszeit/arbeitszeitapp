from arbeitszeit_web.api_presenters.interfaces import FieldTypes, Namespace


class list_plans_presenter:
    def __init__(self, namespace: Namespace, fields: FieldTypes) -> None:
        self.namespace = namespace
        self.plan_model = self.namespace.model(
            name="Plan",
            model={
                "plan_id": fields.string,
                "company_name": fields.string,
                "company_id": fields.string,
                "product_name": fields.string,
                "description": fields.string,
                "price_per_unit": fields.decimal,
            },
        )
        self.model = self.namespace.model(
            name="PlanList",
            model={"results": fields.nested(model=self.plan_model, as_list=True)},
        )

    def __call__(self, original_function):
        @self.namespace.marshal_with(self.model)
        def wrapped_function(*args, **kwargs):
            return original_function(*args, **kwargs)

        return wrapped_function
