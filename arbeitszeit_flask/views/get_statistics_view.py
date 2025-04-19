from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from arbeitszeit.use_cases.get_statistics import GetStatisticsUseCase
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.get_statistics_presenter import (
    GetStatisticsPresenter,
)


@dataclass
class GetStatisticsView:
    get_statistics_use_case: GetStatisticsUseCase
    presenter: GetStatisticsPresenter

    def GET(self) -> Response:
        use_case_response = self.get_statistics_use_case.get_statistics()
        view_model = self.presenter.present(use_case_response)
        return FlaskResponse(
            render_template("user/statistics.html", view_model=view_model)
        )
