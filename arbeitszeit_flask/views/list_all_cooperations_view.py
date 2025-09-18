from dataclasses import dataclass

from flask import render_template

from arbeitszeit.interactors.list_all_cooperations import ListAllCooperationsInteractor
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.list_all_cooperations_presenter import (
    ListAllCooperationsPresenter,
)


@dataclass
class ListAllCooperationsView:
    interactor: ListAllCooperationsInteractor
    presenter: ListAllCooperationsPresenter

    def GET(self) -> Response:
        response = self.interactor.execute()
        view_model = self.presenter.present(response)
        return render_template("user/list_all_cooperations.html", view_model=view_model)
