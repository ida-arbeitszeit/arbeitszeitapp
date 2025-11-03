from __future__ import annotations

from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, url_for

from arbeitszeit.interactors.invite_worker_to_company import (
    InviteWorkerToCompanyInteractor,
)
from arbeitszeit.interactors.list_workers import ListWorkersInteractor
from arbeitszeit_db import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.types import Response
from arbeitszeit_web.forms import InviteWorkerToCompanyForm
from arbeitszeit_web.www.controllers.invite_worker_to_company_controller import (
    InviteWorkerToCompanyController,
)
from arbeitszeit_web.www.controllers.list_workers_controller import (
    ListWorkersController,
)
from arbeitszeit_web.www.presenters.invite_worker_to_company_presenter import (
    InviteWorkerToCompanyPresenter,
)
from arbeitszeit_web.www.presenters.list_workers_presenter import ListWorkersPresenter

TEMPLATE_NAME = "company/invite_worker_to_company.html"


@dataclass
class InviteWorkerToCompanyView:
    list_workers_controller: ListWorkersController
    list_workers_interactor: ListWorkersInteractor
    list_workers_presenter: ListWorkersPresenter
    invite_worker_controller: InviteWorkerToCompanyController
    invite_worker_interactor: InviteWorkerToCompanyInteractor
    invite_worker_presenter: InviteWorkerToCompanyPresenter

    def GET(self) -> Response:
        list_workers_interactor_request = (
            self.list_workers_controller.create_interactor_request()
        )
        list_workers_interactor_response = self.list_workers_interactor.execute(
            list_workers_interactor_request
        )
        list_workers_view_model = self.list_workers_presenter.show_workers_list(
            list_workers_interactor_response
        )
        return FlaskResponse(
            render_template(
                TEMPLATE_NAME,
                form=InviteWorkerToCompanyForm(""),
                view_model=list_workers_view_model,
            )
        )

    @commit_changes
    def POST(self) -> Response:
        try:
            invite_worker_interactor_request = (
                self.invite_worker_controller.import_request_data(
                    request=FlaskRequest()
                )
            )
        except self.invite_worker_controller.FormError as error:
            return self._handle_failed_invitation(error.form)
        invite_worker_interactor_response = self.invite_worker_interactor.invite_worker(
            invite_worker_interactor_request
        )
        view_model = self.invite_worker_presenter.present(
            invite_worker_interactor_response
        )
        if view_model.status_code == 302:
            return redirect(url_for("main_company.invite_worker_to_company"))
        return self._handle_failed_invitation(
            InviteWorkerToCompanyForm(worker_id_value=view_model.worker)
        )

    def _handle_failed_invitation(self, form: InviteWorkerToCompanyForm) -> Response:
        list_workers_interactor_request = (
            self.list_workers_controller.create_interactor_request()
        )
        list_workers_interactor_response = self.list_workers_interactor.execute(
            list_workers_interactor_request
        )
        list_workers_view_model = self.list_workers_presenter.show_workers_list(
            list_workers_interactor_response
        )
        return FlaskResponse(
            render_template(
                TEMPLATE_NAME,
                form=form,
                view_model=list_workers_view_model,
            ),
            status=400,
        )
