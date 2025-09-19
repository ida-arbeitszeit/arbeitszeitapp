from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, url_for
from flask_login import current_user

from arbeitszeit.interactors import list_workers
from arbeitszeit.interactors.register_hours_worked import RegisterHoursWorkedInteractor
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.register_hours_worked_controller import (
    ControllerRejection,
    RegisterHoursWorkedController,
)
from arbeitszeit_web.www.presenters.register_hours_worked_presenter import (
    RegisterHoursWorkedPresenter,
)


@dataclass
class RegisterHoursWorkedView:
    register_hours_worked: RegisterHoursWorkedInteractor
    controller: RegisterHoursWorkedController
    presenter: RegisterHoursWorkedPresenter
    list_workers: list_workers.ListWorkersInteractor

    def GET(self) -> Response:
        return self.create_response(status=200)

    @commit_changes
    def POST(self) -> Response:
        controller_response = self.controller.create_interactor_request(FlaskRequest())
        if isinstance(controller_response, ControllerRejection):
            self.presenter.present_controller_warnings(controller_response)
            return self.create_response(status=400)
        else:
            interactor_response = self.register_hours_worked.execute(
                controller_response
            )
            status_code = self.presenter.present_interactor_response(
                interactor_response
            )
            if status_code == 302:
                return redirect(url_for("main_company.register_hours_worked"))
            return self.create_response(status=status_code)

    def create_response(self, status: int) -> Response:
        workers_list = self.list_workers.execute(
            list_workers.Request(company=UUID(current_user.id))
        )
        return FlaskResponse(
            render_template(
                "company/register_hours_worked.html",
                workers_list=workers_list.workers,
            ),
            status=status,
        )
