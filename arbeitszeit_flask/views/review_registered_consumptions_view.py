from dataclasses import dataclass

import flask

from arbeitszeit.interactors.review_registered_consumptions import (
    ReviewRegisteredConsumptionsInteractor,
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
    interactor: ReviewRegisteredConsumptionsInteractor
    presenter: ReviewRegisteredConsumptionsPresenter

    def GET(self) -> types.Response:
        interactor_request = self.controller.create_interactor_request()
        match interactor_request:
            case InvalidRequest(status_code=status_code):
                return flask.Response(status=status_code)
        interactor_response = self.interactor.review_registered_consumptions(
            interactor_request
        )
        view_model = self.presenter.present(interactor_response)
        return flask.Response(
            flask.render_template(
                "company/review_registered_consumptions.html",
                view_model=view_model,
            )
        )
