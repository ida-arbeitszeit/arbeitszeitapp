from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.query_companies import (
    QueryCompanies as QueryCompaniesUseCase,
)
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.api.response_documentation import with_response_documentation
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.query_companies_api_controller import (
    QueryCompaniesApiController,
)
from arbeitszeit_web.api_presenters.query_companies_api_presenter import (
    QueryCompaniesApiPresenter,
)
from arbeitszeit_web.api_presenters.response_errors import BadRequest

namespace = Namespace("companies", "Companies related endpoints.")

input_documentation = generate_input_documentation(
    QueryCompaniesApiController.create_expected_inputs()
)

model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=QueryCompaniesApiPresenter().get_schema()
)


@namespace.route("")
class QueryCompanies(Resource):
    @namespace.expect(input_documentation)
    @namespace.marshal_with(model)
    @with_response_documentation(error_responses=[BadRequest], namespace=namespace)
    @with_injection()
    def get(
        self,
        controller: QueryCompaniesApiController,
        query_companies: QueryCompaniesUseCase,
        presenter: QueryCompaniesApiPresenter,
    ):
        """Query companies."""
        use_case_request = controller.create_request()
        response = query_companies(use_case_request)
        view_model = presenter.create_view_model(response)
        return view_model
