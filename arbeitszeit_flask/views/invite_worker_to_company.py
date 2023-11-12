from __future__ import annotations

from dataclasses import dataclass

from flask import Response, flash, render_template

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit.use_cases.list_workers import ListWorkers
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import InviteWorkerToCompanyForm
from arbeitszeit_web.www.controllers.invite_worker_to_company_controller import (
    InviteWorkerToCompanyController,
)
from arbeitszeit_web.www.controllers.list_workers_controller import (
    ListWorkersController,
)
from arbeitszeit_web.www.presenters.invite_worker_to_company_presenter import (
    InviteWorkerToCompanyPresenter,
    ViewModel,
)
from arbeitszeit_web.www.presenters.list_workers_presenter import ListWorkersPresenter


@dataclass
class InviteWorkerToCompanyView:
    post_request_handler: InviteWorkerPostRequestHandler
    get_request_handler: InviteWorkerGetRequestHandler

    def respond_to_get(self, form: InviteWorkerToCompanyForm) -> Response:
        return self.get_request_handler.respond_to_get(form)

    def respond_to_post(self, form: InviteWorkerToCompanyForm) -> Response:
        return self.post_request_handler.respond_to_post(form)


@dataclass
class InviteWorkerGetRequestHandler:
    controller: ListWorkersController
    use_case: ListWorkers
    presenter: ListWorkersPresenter

    def respond_to_get(self, form: InviteWorkerToCompanyForm) -> Response:
        template_name = "company/invite_worker_to_company.html"
        use_case_request = self.controller.create_use_case_request()
        use_case_response = self.use_case(use_case_request)
        view_model = self.presenter.show_workers_list(use_case_response)
        return Response(
            render_template(
                template_name,
                form=form,
                view_model=view_model,
            )
        )


@dataclass
class InviteWorkerPostRequestHandler:
    use_case: InviteWorkerToCompanyUseCase
    presenter: InviteWorkerToCompanyPresenter
    controller: InviteWorkerToCompanyController

    @commit_changes
    def respond_to_post(self, form: InviteWorkerToCompanyForm) -> Response:
        template_name = "company/invite_worker_to_company.html"
        if not form.validate():
            return self._display_form_errors(form, template_name)
        try:
            use_case_request = self.controller.import_request_data(form)
        except ValueError:
            return self._display_form_errors(form, template_name)
        use_case_response = self.use_case(use_case_request)
        view_model = self.presenter.present(use_case_response)
        for notification in view_model.notifications:
            flash(notification)
        return Response(
            render_template(template_name, form=form, view_model=view_model),
            status=200,
        )

    def _display_form_errors(
        self, form: InviteWorkerToCompanyForm, template_name: str
    ) -> Response:
        view_model = ViewModel(notifications=["Ungültiges Formular"])
        return Response(
            render_template(template_name, form=form, view_model=view_model),
            status=400,
        )
