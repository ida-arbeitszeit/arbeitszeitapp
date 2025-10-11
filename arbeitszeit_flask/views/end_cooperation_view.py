from dataclasses import dataclass

from flask import redirect

from arbeitszeit.interactors.end_cooperation import EndCooperationInteractor
from arbeitszeit_db import commit_changes
from arbeitszeit_flask import types
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from arbeitszeit_web.www.presenters.end_cooperation_presenter import (
    EndCooperationPresenter,
)


@dataclass
class EndCooperationView:
    interactor: EndCooperationInteractor
    controller: EndCooperationController
    presenter: EndCooperationPresenter

    @commit_changes
    def POST(self) -> types.Response:
        request = FlaskRequest()
        interactor_request = self.controller.process_request_data(request=request)
        if interactor_request is None:
            return http_404()
        interactor_response = self.interactor.execute(interactor_request)
        view_model = self.presenter.present(interactor_response, web_request=request)
        if view_model.show_404:
            return http_404()
        return redirect(view_model.redirect_url)
