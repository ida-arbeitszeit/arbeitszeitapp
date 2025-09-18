from dataclasses import dataclass
from typing import cast
from uuid import UUID

from flask import Response, redirect, render_template, request

from arbeitszeit.interactors.answer_company_work_invite import (
    AnswerCompanyWorkInviteInteractor,
    AnswerCompanyWorkInviteRequest,
)
from arbeitszeit.interactors.show_company_work_invite_details import (
    ShowCompanyWorkInviteDetailsInteractor,
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
    details_interactor: ShowCompanyWorkInviteDetailsInteractor
    details_presenter: ShowCompanyWorkInviteDetailsPresenter
    details_controller: ShowCompanyWorkInviteDetailsController
    answer_controller: AnswerCompanyWorkInviteController
    answer_presenter: AnswerCompanyWorkInvitePresenter
    answer_interactor: AnswerCompanyWorkInviteInteractor

    def GET(self, invite_id: UUID) -> Response:
        interactor_request = self.details_controller.create_interactor_request(
            invite_id
        )
        if interactor_request is None:
            return http_404()
        interactor_response = self.details_interactor.show_company_work_invite_details(
            interactor_request
        )
        view_model = self.details_presenter.render_response(interactor_response)
        if view_model is None:
            return http_404()
        return Response(
            render_template(TEMPLATE, view_model=view_model),
            status=200,
        )

    @commit_changes
    def POST(self, invite_id: UUID) -> Response:
        form = AnswerCompanyWorkInviteForm(request.form)
        interactor_request = self.answer_controller.import_form_data(
            form=form, invite_id=invite_id
        )
        assert isinstance(interactor_request, AnswerCompanyWorkInviteRequest)
        interactor_response = self.answer_interactor.execute(interactor_request)
        view_model = self.answer_presenter.present(interactor_response)
        return cast(Response, redirect(view_model.redirect_url))
