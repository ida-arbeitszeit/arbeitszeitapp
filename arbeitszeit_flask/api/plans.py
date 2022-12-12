from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.dependency_injection import FlaskApiModule, with_injection
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.fields import Fields
from arbeitszeit_web.api_presenters.list_active_plans_presenter import (
    list_active_plans_presenter_get,
)

namespace = Namespace("plans", "Plan related endpoints.")


@with_injection(modules=[FlaskApiModule()])
def get_get_presenter(namespace: Namespace, fields: Fields):
    return list_active_plans_presenter_get(
        namespace=namespace, fields=fields
    )


@namespace.route("/active")
class ListActivePlans(Resource):
    @get_get_presenter(namespace)
    @with_injection()
    def get(self, controller: QueryPlansApiController, query_plans: QueryPlans):
        """List active plans."""
        use_case_request = controller.get_request()
        response = query_plans(request=use_case_request)
        return response
