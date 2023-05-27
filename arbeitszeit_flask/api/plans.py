from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from arbeitszeit_web.api_presenters.response_errors import BadRequest

namespace = Namespace("plans", "Plan related endpoints.")

input_documentation = generate_input_documentation(
    QueryPlansApiController.create_expected_inputs()
)

model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=QueryPlansApiPresenter().get_schema()
)


@namespace.route("/active")
class ListActivePlans(Resource):
    @namespace.expect(input_documentation)
    @namespace.marshal_with(model)
    @error_response_handling(error_responses=[BadRequest], namespace=namespace)
    @with_injection()
    def get(
        self,
        controller: QueryPlansApiController,
        query_plans: QueryPlans,
        presenter: QueryPlansApiPresenter,
    ):
        """List active plans."""
        use_case_request = controller.create_request()
        response = query_plans(request=use_case_request)
        view_model = presenter.create_view_model(response)
        return view_model
