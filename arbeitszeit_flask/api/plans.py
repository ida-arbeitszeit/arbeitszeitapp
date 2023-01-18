from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.schema_converter import json_schema_to_flaskx
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.interfaces import ApiPresenter
from arbeitszeit_web.api_presenters.plans import ActivePlansPresenter

namespace = Namespace("plans", "Plan related endpoints.")


def register_api_presenter(presenter: ApiPresenter):
    model = json_schema_to_flaskx(schema=presenter.get_schema(), namespace=namespace)
    return namespace.marshal_with(model)


@namespace.route("/active")
class ListActivePlans(Resource):
    @register_api_presenter(ActivePlansPresenter())
    @with_injection()
    def get(self, controller: QueryPlansApiController, query_plans: QueryPlans):
        """List active plans."""
        use_case_request = controller.get_request()
        response = query_plans(request=use_case_request)
        return response