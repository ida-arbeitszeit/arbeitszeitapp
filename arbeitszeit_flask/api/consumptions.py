from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumption,
)
from arbeitszeit_flask.api.authentication import authentication_check
from arbeitszeit_flask.api.input_documentation import with_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api.controllers.liquid_means_consumption_controller import (
    LiquidMeansConsumptionController,
    liquid_means_expected_inputs,
)
from arbeitszeit_web.api.presenters.liquid_means_consumption_presenter import (
    LiquidMeansConsumptionPresenter,
)
from arbeitszeit_web.api.response_errors import (
    BadRequest,
    Forbidden,
    NotFound,
    Unauthorized,
    UnsupportedMediaType,
)

namespace = Namespace("consumptions", "Consumptions related endpoints.")


model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=LiquidMeansConsumptionPresenter().get_schema()
)


@namespace.route("/liquid_means_of_production")
class LiquidMeansOfProduction(Resource):
    @with_input_documentation(
        expected_inputs=liquid_means_expected_inputs, namespace=namespace
    )
    @namespace.marshal_with(model, skip_none=True)
    @error_response_handling(
        error_responses=[
            Unauthorized,
            BadRequest,
            NotFound,
            Forbidden,
            UnsupportedMediaType,
        ],
        namespace=namespace,
    )
    @authentication_check
    @with_injection()
    @commit_changes
    def post(
        self,
        controller: LiquidMeansConsumptionController,
        register_productive_consumption: RegisterProductiveConsumption,
        presenter: LiquidMeansConsumptionPresenter,
    ):
        """
        Register consumption of liquid means of production.
        """
        use_case_request = controller.create_request()
        use_case_response = register_productive_consumption(use_case_request)
        return presenter.create_view_model(use_case_response)
