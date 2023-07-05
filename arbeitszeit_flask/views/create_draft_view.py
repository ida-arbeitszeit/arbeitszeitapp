from dataclasses import dataclass
from typing import Union
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect

from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit_flask.forms import CreateDraftForm
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.http_404_view import Http404View
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
    template_renderer: UserTemplateRenderer
    http_404_view: Http404View
    url_index: GeneralUrlIndex

    def respond_to_post(self, form: CreateDraftForm) -> Response:
        """either cancel plan creation, save draft or file draft."""
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

    def _create_draft(self, form: CreateDraftForm) -> Union[Response, UUID]:
        use_case_request = self.prefilled_data_controller.import_form_data(form)
        response = self.create_draft(use_case_request)
        if response.is_rejected:
            return self.http_404_view.get_response()
        assert response.draft_id
        return response.draft_id

    def respond_to_get(self) -> Response:
        return FlaskResponse(
            self.template_renderer.render_template(
                "company/create_draft.html",
                context=dict(
                    form=CreateDraftForm(),
                    view_model=dict(
                        load_draft_url=GeneralUrlIndex().get_my_plan_drafts_url(),
                        save_draft_url="",
                        cancel_url="",
                    ),
                ),
            )
        )
