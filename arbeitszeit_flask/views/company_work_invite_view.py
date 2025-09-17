from dataclasses import dataclass
from typing import cast
from uuid import UUID

from flask import Response, redirect, render_template, request

from arbeitszeit.use_cases.answer_company_work_invite import (
    AnswerCompanyWorkInviteRequest,
    AnswerCompanyWorkInviteUseCase,
)
from arbeitszeit.use_cases.show_company_work_invite_details import (
    ShowCompanyWorkInviteDetailsUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import AnswerCompanyWorkInviteForm
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.controllers.answer_company_work_invite_controller import (
    AnswerCompanyWorkInviteController,
)
from arbeitszeit_web.www.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)
from arbeitszeit_web.www.presenters.answer_company_work_invite_presenter import (
    AnswerCompanyWorkInvitePresenter,
)
from arbeitszeit_web.www.presenters.show_company_work_invite_details_presenter import (
    ShowCompanyWorkInviteDetailsPresenter,
)

TEMPLATE = "member/show_company_work_invite_details.html"


@dataclass
class CompanyWorkInviteView:
    details_use_case: ShowCompanyWorkInviteDetailsUseCase
    details_presenter: ShowCompanyWorkInviteDetailsPresenter
    details_controller: ShowCompanyWorkInviteDetailsController
    answer_controller: AnswerCompanyWorkInviteController
    answer_presenter: AnswerCompanyWorkInvitePresenter
    answer_use_case: AnswerCompanyWorkInviteUseCase

    def GET(self, invite_id: UUID) -> Response:
        use_case_request = self.details_controller.create_use_case_request(invite_id)
        if use_case_request is None:
            return http_404()
        use_case_response = self.details_use_case.show_company_work_invite_details(
            use_case_request
        )
        view_model = self.details_presenter.render_response(use_case_response)
        if view_model is None:
            return http_404()
        return Response(
            render_template(TEMPLATE, view_model=view_model),
            status=200,
        )

    @commit_changes
    def POST(self, invite_id: UUID) -> Response:
        form = AnswerCompanyWorkInviteForm(request.form)
        use_case_request = self.answer_controller.import_form_data(
            form=form, invite_id=invite_id
        )
        assert isinstance(use_case_request, AnswerCompanyWorkInviteRequest)
        use_case_response = self.answer_use_case.execute(use_case_request)
        view_model = self.answer_presenter.present(use_case_response)
        return cast(Response, redirect(view_model.redirect_url))
