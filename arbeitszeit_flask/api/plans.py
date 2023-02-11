from flask import abort
from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.input_converter import expected_inputs_to_flaskx_parser
from arbeitszeit_flask.api.schema_converter import json_schema_to_flaskx
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    NegativeNumberError,
    NotAnIntegerError,
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.plans import ActivePlansPresenter

namespace = Namespace("plans", "Plan related endpoints.")

model = json_schema_to_flaskx(
    schema=ActivePlansPresenter().get_schema(), namespace=namespace
)
parser = expected_inputs_to_flaskx_parser(QueryPlansApiController().expected_inputs)


@namespace.route("/active")
class ListActivePlans(Resource):
    @namespace.expect(parser)
    @namespace.marshal_with(model)
    @with_injection()
    def get(self, controller: QueryPlansApiController, query_plans: QueryPlans):
        """List active plans."""
        try:
            use_case_request = controller.get_request(FlaskRequest())
        except NotAnIntegerError:
            abort(400, "The parameter must be an integer.")
        except NegativeNumberError:
            abort(400, "The parameter must not be be a negative number.")
        response = query_plans(request=use_case_request)
        return response
