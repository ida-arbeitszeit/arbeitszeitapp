from flask import Blueprint, Response, abort, jsonify, request

from arbeitszeit.use_cases.query_plans import QueryPlans
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)
from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)

from ..dependency_injection import with_injection

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.errorhandler(405)
def method_not_allowed(e):
    return jsonify(error=str(e)), 405


@api.route("/plans/active", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@with_injection()
def list_active_plans(
    controller: QueryPlansApiController,
    query_plans: QueryPlans,
    presenter: QueryPlansApiPresenter,
):
    if request.method == "GET":
        use_case_request = controller.get_request()
        response = query_plans(request=use_case_request)
        json_string = presenter.get_json(response)
        return Response(json_string, mimetype="application/json")
    elif request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        abort(405)
