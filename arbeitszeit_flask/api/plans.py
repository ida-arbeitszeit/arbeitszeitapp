from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.fields import FieldTypes
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.plans import list_plans_presenter

namespace = Namespace("plans", "Plan related endpoints.")


@namespace.route("/active")
class ListActivePlans(Resource):
    @list_plans_presenter(namespace, FieldTypes())
    @with_injection()
    def get(self, controller: QueryPlansApiController, query_plans: QueryPlans):
        """List active plans."""
        use_case_request = controller.get_request()
        response = query_plans(request=use_case_request)
        return response
