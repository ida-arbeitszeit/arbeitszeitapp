from dataclasses import dataclass

from flask import redirect

from arbeitszeit.use_cases.end_cooperation import EndCooperation
from arbeitszeit_flask import types
from arbeitszeit_flask.database import commit_changes
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
    end_cooperation: EndCooperation
    controller: EndCooperationController
    presenter: EndCooperationPresenter

    @commit_changes
    def POST(self) -> types.Response:
        use_case_request = self.controller.process_request_data(request=FlaskRequest())
        if use_case_request is None:
            return http_404()
        use_case_response = self.end_cooperation(use_case_request)
        view_model = self.presenter.present(use_case_response)
        if view_model.show_404:
            return http_404()
        return redirect(view_model.redirect_url)
