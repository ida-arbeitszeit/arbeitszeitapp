from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from arbeitszeit.use_cases.create_cooperation import (
    CreateCooperation,
    CreateCooperationRequest,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import CreateCooperationForm
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.create_cooperation_presenter import (
    CreateCooperationPresenter,
)


@dataclass
class CreateCooperationView:
    create_cooperation: CreateCooperation
    presenter: CreateCooperationPresenter
    session: FlaskSession

    def GET(self) -> Response:
        return FlaskResponse(self._render_template(CreateCooperationForm()), status=200)

    @commit_changes
    def POST(self) -> Response:
        form = CreateCooperationForm(request.form)
        name = form.get_name_string()
        definition = form.get_definition_string()
        user = self.session.get_current_user()
        assert name
        assert definition
        assert user
        use_case_request = CreateCooperationRequest(user, name, definition)
        use_case_response = self.create_cooperation(use_case_request)
        self.presenter.present(use_case_response)
        if use_case_response.is_rejected:
            return FlaskResponse(self._render_template(form), status=400)
        return redirect(url_for("main_company.my_cooperations"))

    def _render_template(self, form: CreateCooperationForm) -> str:
        return render_template("company/create_cooperation.html", form=form)
