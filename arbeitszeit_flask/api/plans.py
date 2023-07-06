from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.authentication_helper import authentication_check
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api.controllers.get_plan_api_controller import GetPlanApiController
from arbeitszeit_web.api.controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api.presenters.get_plan_api_presenter import GetPlanApiPresenter
from arbeitszeit_web.api.presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from arbeitszeit_web.api.response_errors import BadRequest, NotFound, Unauthorized

namespace = Namespace("plans", "Plan related endpoints.")

active_plans_get_input_documentation = generate_input_documentation(
    QueryPlansApiController.create_expected_inputs()
)

active_plans_get_model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=QueryPlansApiPresenter().get_schema()
)


@namespace.route("/active")
class ActivePlans(Resource):
    @namespace.expect(active_plans_get_input_documentation)
    @namespace.marshal_with(active_plans_get_model, skip_none=True)
    @error_response_handling(
        error_responses=[BadRequest, Unauthorized], namespace=namespace
    )
    @authentication_check
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


plan_get_model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=GetPlanApiPresenter().get_schema()
)


@namespace.route("/<plan_id>")
class Plan(Resource):
    @namespace.marshal_with(plan_get_model, skip_none=True)
    @error_response_handling(
        error_responses=[BadRequest, NotFound], namespace=namespace
    )
    @with_injection()
    def get(
        self,
        plan_id: str,
        controller: GetPlanApiController,
        use_case: GetPlanSummaryUseCase,
        presenter: GetPlanApiPresenter,
    ):
        """Get plan summary."""
        use_case_request = controller.create_request(plan_id)
        use_case_response = use_case.get_plan_summary(use_case_request)
        view_model = presenter.create_view_model(use_case_response)
        return view_model
