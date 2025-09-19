from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template

from arbeitszeit.interactors import create_plan_draft
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.http_error_view import http_403
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.www.controllers.create_draft_controller import (
    CreateDraftController,
)


@dataclass
class CreateDraftView:
    notifier: Notifier
    translator: Translator
    controller: CreateDraftController
    interactor: create_plan_draft.CreatePlanDraft
    url_index: GeneralUrlIndex

    def GET(self) -> Response:
        form = DraftForm(
            product_name_value="",
            description_value="",
            timeframe_value="",
            unit_of_distribution_value="",
            amount_value="",
            means_cost_value="",
            resource_cost_value="",
            labour_cost_value="",
            is_public_plan_value="",
        )
        return self._render_form(form, status_code=200)

    @commit_changes
    def POST(self) -> Response:
        match self.controller.import_form_data(FlaskRequest()):
            case create_plan_draft.Request() as interactor_request:
                pass
            case DraftForm() as form:
                return self._render_form(form, status_code=400)
        response = self.interactor.create_draft(interactor_request)
        if response.is_rejected:
            return http_403()
        self.notifier.display_info(self.translator.gettext("Draft successfully saved."))
        return redirect(self.url_index.get_my_plan_drafts_url())

    def _render_form(self, form: DraftForm, status_code: int) -> Response:
        return FlaskResponse(
            render_template(
                "company/create_draft.html",
                form=form,
                cancel_url=self.url_index.get_my_plan_drafts_url(),
            ),
            status=status_code,
        )
