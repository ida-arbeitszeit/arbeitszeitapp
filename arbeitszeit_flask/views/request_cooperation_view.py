from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.use_cases.list_active_plans_of_company import ListActivePlansOfCompany
from arbeitszeit.use_cases.request_cooperation import RequestCooperation
from arbeitszeit_flask.forms import RequestCooperationForm
from arbeitszeit_web.malformed_input_data import MalformedInputData
from arbeitszeit_web.www.controllers.request_cooperation_controller import (
    RequestCooperationController,
)
from arbeitszeit_web.www.presenters.list_plans_presenter import ListPlansPresenter
from arbeitszeit_web.www.presenters.request_cooperation_presenter import (
    RequestCooperationPresenter,
)

from .http_404_view import Http404View


@dataclass
class RequestCooperationView:
    current_user_id: UUID
    form: RequestCooperationForm
    list_plans: ListActivePlansOfCompany
    list_plans_presenter: ListPlansPresenter
    request_cooperation: RequestCooperation
    controller: RequestCooperationController
    presenter: RequestCooperationPresenter
    not_found_view: Http404View
    template_name: str

    def respond_to_get(self) -> Response:
        list_plans_view_model = self._get_list_plans_view_model()
        return Response(
            render_template(
                self.template_name,
                list_plans_view_model=list_plans_view_model,
            )
        )

    def respond_to_post(self) -> Response:
        list_plans_view_model = self._get_list_plans_view_model()
        use_case_request = self.controller.import_form_data(self.form)
        if use_case_request is None:
            return self.not_found_view.get_response()
        if isinstance(use_case_request, MalformedInputData):
            return self._handle_malformed_data(use_case_request)
        use_case_response = self.request_cooperation(use_case_request)
        view_model = self.presenter.present(use_case_response)
        return Response(
            render_template(
                self.template_name,
                view_model=view_model,
                list_plans_view_model=list_plans_view_model,
            )
        )

    def _handle_malformed_data(self, result: MalformedInputData) -> Response:
        field = getattr(self.form, result.field)
        field.errors += (result.message,)
        return Response(
            render_template(self.template_name, form=self.form),
            status=400,
        )

    def _get_list_plans_view_model(self):
        plans_list_response = self.list_plans(self.current_user_id)
        list_plans_view_model = self.list_plans_presenter.present(plans_list_response)
        return list_plans_view_model
