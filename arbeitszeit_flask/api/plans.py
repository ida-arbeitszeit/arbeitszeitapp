from flask import abort
from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.schema_converter import json_schema_to_flaskx
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.errors import (
    NegativeNumberError,
    NotAnIntegerError,
)
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)

namespace = Namespace("plans", "Plan related endpoints.")

input_documentation = generate_input_documentation(
    QueryPlansApiController.create_expected_inputs()
)

model = json_schema_to_flaskx(
    schema=QueryPlansApiPresenter().get_schema(), namespace=namespace
)


@namespace.route("/active")
class ListActivePlans(Resource):
    @namespace.expect(input_documentation)
    @namespace.marshal_with(model)
    @with_injection()
    def get(
        self,
        controller: QueryPlansApiController,
        query_plans: QueryPlans,
        presenter: QueryPlansApiPresenter,
    ):
        """List active plans."""
        try:
            use_case_request = controller.create_request()
        except NotAnIntegerError:
            abort(400, "The parameter must be an integer.")
        except NegativeNumberError:
            abort(400, "The parameter must not be be a negative number.")
        response = query_plans(request=use_case_request)
        view_model = presenter.create_view_model(response)
        return view_model
