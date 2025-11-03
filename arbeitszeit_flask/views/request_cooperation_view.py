from dataclasses import dataclass

from flask import Response, render_template, request

from arbeitszeit.interactors.list_active_plans_of_company import (
    ListActivePlansOfCompanyInteractor,
)
from arbeitszeit.interactors.request_cooperation import RequestCooperationInteractor
from arbeitszeit_db import commit_changes
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import RequestCooperationForm
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.malformed_input_data import MalformedInputData
from arbeitszeit_web.www.controllers.request_cooperation_controller import (
    RequestCooperationController,
)
from arbeitszeit_web.www.presenters.list_plans_presenter import ListPlansPresenter
from arbeitszeit_web.www.presenters.request_cooperation_presenter import (
    RequestCooperationPresenter,
)

TEMPLATE_NAME = "company/request_cooperation.html"


@dataclass
class RequestCooperationView:
    list_plans: ListActivePlansOfCompanyInteractor
    list_plans_presenter: ListPlansPresenter
    request_cooperation: RequestCooperationInteractor
    controller: RequestCooperationController
    presenter: RequestCooperationPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        list_plans_view_model = self._get_list_plans_view_model()
        return Response(
            render_template(
                TEMPLATE_NAME,
                list_plans_view_model=list_plans_view_model,
            )
        )

    @commit_changes
    def POST(self) -> Response:
        form = RequestCooperationForm(request.form)
        list_plans_view_model = self._get_list_plans_view_model()
        interactor_request = self.controller.import_form_data(form)
        if interactor_request is None:
            return http_404()
        if isinstance(interactor_request, MalformedInputData):
            return self._handle_malformed_data(interactor_request, form)
        interactor_response = self.request_cooperation.execute(interactor_request)
        view_model = self.presenter.present(interactor_response)
        return Response(
            render_template(
                TEMPLATE_NAME,
                view_model=view_model,
                list_plans_view_model=list_plans_view_model,
            )
        )

    def _handle_malformed_data(
        self, result: MalformedInputData, form: RequestCooperationForm
    ) -> Response:
        field = getattr(form, result.field)
        field.errors += (result.message,)
        return Response(
            render_template(TEMPLATE_NAME, form=form),
            status=400,
        )

    def _get_list_plans_view_model(self):
        current_user = self.flask_session.get_current_user()
        assert current_user
        plans_list_response = self.list_plans.execute(current_user)
        list_plans_view_model = self.list_plans_presenter.present(plans_list_response)
        return list_plans_view_model
