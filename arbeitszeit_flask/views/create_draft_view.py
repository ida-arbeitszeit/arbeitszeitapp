from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import CreateDraftForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.http_error_view import http_403
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
    use_case: CreatePlanDraft
    url_index: GeneralUrlIndex

    @commit_changes
    def POST(self) -> Response:
        form = CreateDraftForm(request.form)
        use_case_request = self.controller.import_form_data(form)
        response = self.use_case.create_draft(use_case_request)
        if response.is_rejected:
            return http_403()
        self.notifier.display_info(self.translator.gettext("Draft successfully saved."))
        return redirect(self.url_index.get_my_plan_drafts_url())

    def GET(self) -> Response:
        return FlaskResponse(
            render_template(
                "company/create_draft.html",
                form=CreateDraftForm(),
                cancel_url=self.url_index.get_my_plan_drafts_url(),
            )
        )
