from dataclasses import dataclass
from uuid import UUID

from flask import Response

from arbeitszeit.use_cases import AnswerCompanyWorkInvite
from arbeitszeit_web.answer_company_work_invite import (
    AnswerCompanyWorkInviteController,
    AnswerCompanyWorkInviteForm,
    AnswerCompanyWorkInvitePresenter,
    AnswerCompanyWorkInviteRequest,
)

from .http_404_view import Http404View


@dataclass
class AnswerCompanyWorkInviteView:
    controller: AnswerCompanyWorkInviteController
    presenter: AnswerCompanyWorkInvitePresenter
    use_case: AnswerCompanyWorkInvite
    http_404_view: Http404View

    def respond_to_get(
        self, form: AnswerCompanyWorkInviteForm, invite_id: UUID
    ) -> Response:
        use_case_request = self.controller.import_form_data(
            form=form, invite_id=invite_id
        )
        assert isinstance(use_case_request, AnswerCompanyWorkInviteRequest)
        use_case_response = self.use_case(use_case_request)
        if use_case_response.is_success:
            return Response(status=200)
        else:
            if (
                use_case_response.failure_reason
                == use_case_response.Failure.invite_not_found
            ):
                return self.http_404_view.get_response()
            else:
                return Response(status=403)
