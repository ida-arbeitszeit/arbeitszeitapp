from flask import Response

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from arbeitszeit_flask.dependency_injection import with_injection
from flask_restx import Namespace, Resource


namespace = Namespace("plans", "Plan related endpoints.")


@namespace.route("/active")
class ListActivePlans(Resource):

    @with_injection()
    def get(
        self,
        controller: QueryPlansApiController,
        query_plans: QueryPlans,
        presenter: QueryPlansApiPresenter,
    ):
        """List active plans."""
        use_case_request = controller.get_request()
        response = query_plans(request=use_case_request)
        json_string = presenter.get_json(response)
        return Response(json_string, mimetype="application/json")
