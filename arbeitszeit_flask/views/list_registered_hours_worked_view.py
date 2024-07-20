from dataclasses import dataclass

import flask

from arbeitszeit.use_cases.list_registered_hours_worked import (
    ListRegisteredHoursWorkedUseCase,
)
from arbeitszeit_flask import types
from arbeitszeit_web.www.controllers.list_registered_hours_worked_controller import (
    ListRegisteredHoursWorkedController,
)
from arbeitszeit_web.www.presenters.list_registered_hours_worked_presenter import (
    ListRegisteredHoursWorkedPresenter,
)


@dataclass
class ListRegisteredHoursWorkedView:
    controller: ListRegisteredHoursWorkedController
    use_case: ListRegisteredHoursWorkedUseCase
    presenter: ListRegisteredHoursWorkedPresenter

    def GET(self) -> types.Response:
        request = self.controller.create_request()
        response = self.use_case.list_registered_hours_worked(request)
        view_model = self.presenter.present(response)
        return flask.Response(
            flask.render_template(
                "company/list_registered_hours_worked.html",
                view_model=view_model,
            )
        )
