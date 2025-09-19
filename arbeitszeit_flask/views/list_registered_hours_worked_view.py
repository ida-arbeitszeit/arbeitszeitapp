from dataclasses import dataclass

import flask

from arbeitszeit.interactors.list_registered_hours_worked import (
    ListRegisteredHoursWorkedInteractor,
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
    interactor: ListRegisteredHoursWorkedInteractor
    presenter: ListRegisteredHoursWorkedPresenter

    def GET(self) -> types.Response:
        request = self.controller.create_request()
        response = self.interactor.list_registered_hours_worked(request)
        view_model = self.presenter.present(response)
        return flask.Response(
            flask.render_template(
                "company/list_registered_hours_worked.html",
                view_model=view_model,
            )
        )
