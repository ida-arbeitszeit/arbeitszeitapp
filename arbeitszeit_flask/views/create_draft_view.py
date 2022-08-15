from dataclasses import asdict, dataclass
from typing import Union
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, url_for

from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit.use_cases.get_draft_summary import GetDraftSummary
from arbeitszeit.use_cases.get_plan_summary_company import GetPlanSummaryCompany
from arbeitszeit_flask.forms import CreateDraftForm
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_404_view import Http404View
from arbeitszeit_web.create_draft import (
    CreateDraftController,
    GetPrefilledDraftDataPresenter,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class CreateDraftView:
    request: Request
    session: Session
    notifier: Notifier
    translator: Translator
    prefilled_data_controller: CreateDraftController
    get_plan_summary_company: GetPlanSummaryCompany
    create_draft: CreatePlanDraft
    get_draft_summary: GetDraftSummary
    create_draft_presenter: GetPrefilledDraftDataPresenter
    template_renderer: UserTemplateRenderer
    http_404_view: Http404View

    def respond_to_post(self, form: CreateDraftForm) -> Response:
        """either cancel plan creation, save draft or file draft."""

        user_action = self.request.get_form("action")
        if user_action == "save_draft":
            self._create_draft(form)
            self.notifier.display_info(
                self.translator.gettext("Draft successfully saved.")
            )
            return redirect(url_for("main_company.draft_list"))
        elif user_action == "file_draft":
            draft_id = self._create_draft(form)
            return redirect(
                url_for(
                    "main_company.self_approve_plan",
                    draft_uuid=draft_id,
                )
            )
        else:
            self.notifier.display_info(
                self.translator.gettext("Plan creation has been canceled.")
            )
            return redirect(url_for("main_company.my_plans"))

    def _create_draft(self, form: CreateDraftForm) -> Union[Response, UUID]:
        use_case_request = self.prefilled_data_controller.import_form_data(form)
        response = self.create_draft(use_case_request)
        if response.is_rejected:
            return self.http_404_view.get_response()
        assert response.draft_id
        return response.draft_id

    def respond_to_get(self) -> Response:
        """
        show user input form for plan draft.
        prefilled data comes from exired plan or saved draft if available in request arguments.
        """
        query_string = self.request.query_string()
        if expired_plan_id := query_string.get("expired_plan_id"):
            # use expired plan to prefill data
            planner = self.session.get_current_user()
            assert expired_plan_id is not None
            assert planner is not None
            response = self.get_plan_summary_company.get_plan_summary_for_company(
                UUID(expired_plan_id), planner
            )
            if isinstance(response, GetPlanSummaryCompany.Success):
                view_model = self.create_draft_presenter.show_prefilled_draft_data(
                    response.plan_summary
                )
                form = CreateDraftForm(data=asdict(view_model.prefilled_draft_data))
            else:
                return self.http_404_view.get_response()

        else:
            form = CreateDraftForm()

        return FlaskResponse(
            self.template_renderer.render_template(
                "company/create_draft.html",
                context=dict(
                    form=form,
                    view_model=dict(
                        self_approve_plan="",
                        save_draft_url="",
                        cancel_url="",
                    ),
                ),
            )
        )
