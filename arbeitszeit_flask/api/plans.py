from flask_restx import Namespace, Resource

from arbeitszeit.plan_summary import PlanSummaryService
from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.get_plan_api_controller import GetPlanApiController
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.get_plan_api_presenter import GetPlanApiPresenter
from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from arbeitszeit_web.api_presenters.response_errors import BadRequest, NotFound

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
        service: PlanSummaryService,
        presenter: GetPlanApiPresenter,
    ):
        """Get plan summary."""
        plan_uuid = controller.format_input(plan_id)
        plan_summary = service.get_summary_from_plan(plan_uuid)
        view_model = presenter.create_view_model(plan_summary)
        return view_model
