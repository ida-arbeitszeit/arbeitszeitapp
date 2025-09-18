from flask_restx import Namespace, Resource

from arbeitszeit.interactors.query_companies import (
    QueryCompaniesInteractor as QueryCompaniesInteractor,
)
from arbeitszeit_flask.api.authentication import authentication_check
from arbeitszeit_flask.api.input_documentation import with_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_web.api.controllers.query_companies_api_controller import (
    QueryCompaniesApiController,
    query_companies_expected_inputs,
)
from arbeitszeit_web.api.presenters.query_companies_api_presenter import (
    QueryCompaniesApiPresenter,
)
from arbeitszeit_web.api.response_errors import BadRequest, Unauthorized

namespace = Namespace("companies", "Companies related endpoints.")

model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=QueryCompaniesApiPresenter().get_schema()
)


@namespace.route("")
class QueryCompanies(Resource):
    @with_input_documentation(
        expected_inputs=query_companies_expected_inputs, namespace=namespace
    )
    @namespace.marshal_with(model, skip_none=True)
    @error_response_handling(
        error_responses=[BadRequest, Unauthorized], namespace=namespace
    )
    @authentication_check
    @with_injection()
    def get(
        self,
        controller: QueryCompaniesApiController,
        query_companies: QueryCompaniesInteractor,
        presenter: QueryCompaniesApiPresenter,
    ):
        """Query companies."""
        interactor_request = controller.create_request(FlaskRequest())
        response = query_companies.execute(interactor_request)
        view_model = presenter.create_view_model(response)
        return view_model
