from dataclasses import dataclass

from flask import render_template

from arbeitszeit.use_cases.list_all_cooperations import ListAllCooperations
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.list_all_cooperations_presenter import (
    ListAllCooperationsPresenter,
)


@dataclass
class ListAllCooperationsView:
    use_case: ListAllCooperations
    presenter: ListAllCooperationsPresenter

    def GET(self) -> Response:
        response = self.use_case()
        view_model = self.presenter.present(response)
        return render_template("user/list_all_cooperations.html", view_model=view_model)
