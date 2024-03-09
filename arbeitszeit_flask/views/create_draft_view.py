from dataclasses import dataclass
from typing import Union
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import CreateDraftForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.www.controllers.create_draft_controller import (
    CreateDraftController,
)


@dataclass
class CreateDraftView:
    request: Request
    notifier: Notifier
    translator: Translator
    prefilled_data_controller: CreateDraftController
    create_draft: CreatePlanDraft
    url_index: GeneralUrlIndex

    @commit_changes
    def POST(self) -> Response:
        form = CreateDraftForm(request.form)
        user_action = self.request.get_form("action")
        if user_action == "save_draft":
            self._create_draft(form)
            self.notifier.display_info(
                self.translator.gettext("Draft successfully saved.")
            )
            return redirect(self.url_index.get_my_plan_drafts_url())
        else:
            self.notifier.display_info(
                self.translator.gettext("Plan creation has been canceled.")
            )
            return redirect(self.url_index.get_my_plan_drafts_url())

    def GET(self) -> Response:
        return FlaskResponse(
            render_template(
                "company/create_draft.html",
                form=CreateDraftForm(),
                view_model=dict(
                    load_draft_url=GeneralUrlIndex().get_my_plan_drafts_url(),
                    save_draft_url="",
                    cancel_url="",
                ),
            )
        )

    def _create_draft(self, form: CreateDraftForm) -> Union[Response, UUID]:
        use_case_request = self.prefilled_data_controller.import_form_data(form)
        response = self.create_draft(use_case_request)
        if response.is_rejected:
            return http_404()
        assert response.draft_id
        return response.draft_id
