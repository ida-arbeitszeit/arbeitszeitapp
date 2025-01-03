from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.edit_draft import EditDraftUseCase
from arbeitszeit.use_cases.get_draft_details import GetDraftDetails
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import CreateDraftForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.controllers.edit_draft_controller import EditDraftController
from arbeitszeit_web.www.presenters.edit_draft_presenter import EditDraftPresenter
from arbeitszeit_web.www.presenters.get_draft_details_presenter import (
    GetDraftDetailsPresenter,
)


@dataclass
class DraftDetailsView:
    use_case: GetDraftDetails
    presenter: GetDraftDetailsPresenter
    edit_draft_use_case: EditDraftUseCase
    edit_draft_controller: EditDraftController
    edit_draft_presenter: EditDraftPresenter
    url_index: GeneralUrlIndex

    def GET(self, draft_id: UUID) -> Response:
        use_case_response = self.use_case(draft_id)
        if use_case_response is None:
            return http_404()
        form = CreateDraftForm()
        view_model = self.presenter.present_draft_details(use_case_response, form=form)
        return FlaskResponse(
            render_template(
                "company/draft_details.html",
                cancel_url=view_model.cancel_url,
                form=form,
            )
        )

    @commit_changes
    def POST(self, draft_id: UUID) -> Response:
        form = CreateDraftForm(request.form)
        if not form.validate():
            return self._handle_invalid_submission(form, status=400)
        use_case_request = self.edit_draft_controller.process_form(
            form=form,
            draft_id=draft_id,
        )
        if use_case_request is None:
            return self._handle_invalid_submission(form, status=400)
        use_case_response = self.edit_draft_use_case.edit_draft(use_case_request)
        view_model = self.edit_draft_presenter.render_response(use_case_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        else:
            return self._handle_invalid_submission(form, status=404)

    def _handle_invalid_submission(
        self, form: CreateDraftForm, status: int
    ) -> Response:
        return FlaskResponse(
            render_template(
                "company/draft_details.html",
                cancel_url=self.url_index.get_my_plans_url(),
                form=form,
            ),
            status=status,
        )
