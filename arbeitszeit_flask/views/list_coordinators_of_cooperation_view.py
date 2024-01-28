from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase,
)
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.list_coordinations_of_cooperation_presenter import (
    ListCoordinationsOfCooperationPresenter,
)


@dataclass
class ListCoordinationsOfCooperationView:
    list_coordinations_of_cooperation: ListCoordinationsOfCooperationUseCase
    presenter: ListCoordinationsOfCooperationPresenter

    def GET(self, coop_id: UUID) -> Response:
        use_case_response = self.list_coordinations_of_cooperation.list_coordinations(
            ListCoordinationsOfCooperationUseCase.Request(cooperation=coop_id)
        )
        view_model = self.presenter.list_coordinations_of_cooperation(use_case_response)
        return render_template(
            "user/list_coordinations_of_cooperation.html",
            view_model=view_model,
        )
