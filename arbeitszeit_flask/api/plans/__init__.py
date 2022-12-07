from dataclasses import asdict

from flask_restx import Namespace, Resource, fields

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)

namespace = Namespace("plans", "Plan related endpoints.")


plan_model = namespace.model(
    "Plan",
    {
        "plan_id": fields.String,
        "company_name": fields.String,
        "activation_date": fields.DateTime(dt_format="iso8601"),
    },
)

plan_list_model = namespace.model(
    "PlanList", {"results": fields.Nested(model=plan_model, as_list=True)}
)


@namespace.route("/active")
class ListActivePlans(Resource):
    @namespace.marshal_with(plan_list_model)
    @with_injection()
    def get(
        self,
        controller: QueryPlansApiController,
        query_plans: QueryPlans,
    ):
        """List active plans."""
        use_case_request = controller.get_request()
        response = query_plans(request=use_case_request)
        return asdict(response)
