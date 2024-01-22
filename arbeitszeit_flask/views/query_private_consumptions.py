from dataclasses import dataclass

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


@dataclass
class QueryPrivateConsumptionsView:
    controller: QueryPrivateConsumptionsController
    use_case: QueryPrivateConsumptions
    presenter: PrivateConsumptionsPresenter

    def GET(self) -> Response:
        uc_request = self.controller.process_request()
        match uc_request:
            case InvalidRequest(status_code=status_code):
                return flask.Response(status=status_code)
        response = self.use_case.query_private_consumptions(uc_request)
        view_model = self.presenter.present_private_consumptions(response)
        return flask.Response(
            flask.render_template(
                "member/consumptions.html",
                view_model=view_model,
            )
        )
