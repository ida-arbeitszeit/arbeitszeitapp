from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template

from arbeitszeit.interactors import edit_draft
from arbeitszeit.interactors.get_draft_details import GetDraftDetailsInteractor
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.www.controllers.edit_draft_controller import EditDraftController
from arbeitszeit_web.www.presenters.edit_draft_presenter import EditDraftPresenter
from arbeitszeit_web.www.presenters.get_draft_details_presenter import (
    GetDraftDetailsPresenter,
)


@dataclass
class DraftDetailsView:
    interactor: GetDraftDetailsInteractor
    presenter: GetDraftDetailsPresenter
    edit_draft_interactor: edit_draft.EditDraftInteractor
    edit_draft_controller: EditDraftController
    edit_draft_presenter: EditDraftPresenter
    url_index: GeneralUrlIndex

    def GET(self, draft_id: UUID) -> Response:
        interactor_response = self.interactor.execute(draft_id)
        if interactor_response is None:
            return http_404()
        view_model = self.presenter.present_draft_details(interactor_response)
        return FlaskResponse(
            render_template(
                "company/draft_details.html",
                cancel_url=view_model.cancel_url,
                form=view_model.form,
            )
        )

    @commit_changes
    def POST(self, draft_id: UUID) -> Response:
        match self.edit_draft_controller.process_form(
            request=FlaskRequest(),
            draft_id=draft_id,
        ):
            case edit_draft.Request() as interactor_request:
                pass
            case DraftForm() as form:
                return self._handle_invalid_submission(form, status=400)
        interactor_response = self.edit_draft_interactor.edit_draft(interactor_request)
        view_model = self.edit_draft_presenter.render_response(interactor_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        else:
            return http_404()

    def _handle_invalid_submission(self, form: DraftForm, status: int) -> Response:
        return FlaskResponse(
            render_template(
                "company/draft_details.html",
                cancel_url=self.url_index.get_my_plans_url(),
                form=form,
            ),
            status=status,
        )
