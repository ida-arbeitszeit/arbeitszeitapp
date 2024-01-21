import flask

from arbeitszeit.use_cases.query_private_consumptions import QueryPrivateConsumptions
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.query_private_consumptions_controller import (
    InvalidRequest,
    QueryPrivateConsumptionsController,
)
from arbeitszeit_web.www.presenters.private_consumptions_presenter import (
    PrivateConsumptionsPresenter,
)


def consumptions(
    controller: QueryPrivateConsumptionsController,
    use_case: QueryPrivateConsumptions,
    presenter: PrivateConsumptionsPresenter,
) -> Response:
    uc_request = controller.process_request()
    match uc_request:
        case InvalidRequest(status_code=status_code):
            return flask.Response(status=status_code)
    response = use_case.query_private_consumptions(uc_request)
    view_model = presenter.present_private_consumptions(response)
    return flask.Response(
        flask.render_template(
            "member/consumptions.html",
            view_model=view_model,
        )
    )
