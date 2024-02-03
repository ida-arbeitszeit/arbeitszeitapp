from dataclasses import dataclass

import flask

from arbeitszeit.use_cases.review_registered_consumptions import (
    ReviewRegisteredConsumptionsUseCase,
)
from arbeitszeit_flask import types
from arbeitszeit_web.www.controllers.review_registered_consumptions_controller import (
    InvalidRequest,
    ReviewRegisteredConsumptionsController,
)
from arbeitszeit_web.www.presenters.review_registered_consumptions_presenter import (
    ReviewRegisteredConsumptionsPresenter,
)


@dataclass
class ReviewRegisteredConsumptionsView:
    controller: ReviewRegisteredConsumptionsController
    use_case: ReviewRegisteredConsumptionsUseCase
    presenter: ReviewRegisteredConsumptionsPresenter

    def GET(self) -> types.Response:
        use_case_request = self.controller.create_use_case_request()
        match use_case_request:
            case InvalidRequest(status_code=status_code):
                return flask.Response(status=status_code)
        use_case_response = self.use_case.review_registered_consumptions(
            use_case_request
        )
        view_model = self.presenter.present(use_case_response)
        return flask.Response(
            flask.render_template(
                "company/review_registered_consumptions.html",
                view_model=view_model,
            )
        )
