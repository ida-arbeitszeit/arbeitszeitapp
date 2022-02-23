from dataclasses import dataclass

from flask import redirect

from arbeitszeit.use_cases.end_cooperation import EndCooperation
from arbeitszeit_flask import types
from arbeitszeit_flask.views.http_404_view import Http404View
from arbeitszeit_web.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter


@dataclass
class EndCooperationView:
    end_cooperation: EndCooperation
    controller: EndCooperationController
    presenter: EndCooperationPresenter
    http_404_view: Http404View

    def respond_to_get(self) -> types.Response:
        use_case_request = self.controller.process_request_data()
        if use_case_request is None:
            return self.http_404_view.get_response()
        use_case_response = self.end_cooperation(use_case_request)
        view_model = self.presenter.present(use_case_response)
        if view_model.show_404:
            return self.http_404_view.get_response()
        return redirect(view_model.redirect_url)
