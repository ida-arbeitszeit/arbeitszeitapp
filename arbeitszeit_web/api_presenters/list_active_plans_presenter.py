from arbeitszeit_web.api_presenters.fields import Fields

from .namespace import Namespace


class list_active_plans_presenter_get:
    def __init__(
        self,
        namespace: Namespace,
        fields: Fields,
    ) -> None:
        self.namespace = namespace
        self.plan_fields = {
            "plan_id": fields.string_field,
            "company_name": fields.string_field,
            "company_id": fields.string_field,
            "product_name": fields.string_field,
            "description": fields.string_field,
            "price_per_unit": fields.decimal_field,
            "is_public_service": fields.boolean_field,
            "is_available": fields.boolean_field,
            "is_cooperating": fields.boolean_field,
            "activation_date": fields.datetime_field,
        }
        self.plan_model = self.namespace.model(name="Plan", model=self.plan_fields)
        self.plan_list = {
            "results": fields.nested_list_field(
                model=self.plan_model, as_list=True
            )
        }
        self.model = self.namespace.model(name="PlanList", model=self.plan_list)

    def __call__(self, original_function):
        @self.namespace.marshal_with(self.model)
        def wrapped_function(*args, **kwargs):
            return original_function(*args, **kwargs)

        return wrapped_function
