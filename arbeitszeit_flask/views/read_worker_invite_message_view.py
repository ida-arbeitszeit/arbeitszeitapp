from dataclasses import dataclass
from uuid import UUID

from flask import redirect, url_for

from arbeitszeit.use_cases import ReadWorkerInviteMessage
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.read_worker_invite_message import (
    ReadWorkerInviteMessageController,
    ReadWorkerInviteMessagePresenter,
)

from .http_404_view import Http404View


@dataclass
class ReadWorkerInviteMessageView:
    read_message: ReadWorkerInviteMessage
    controller: ReadWorkerInviteMessageController
    presenter: ReadWorkerInviteMessagePresenter
    template_renderer: TemplateRenderer
    http_404_view: Http404View

    def respond_to_get(self, message_id: UUID) -> Response:
        """
        Just setting message as is_read and redirecting
        """
        use_case_request = self.controller.process_request_data(message_id)
        use_case_response = self.read_message(use_case_request)
        if isinstance(use_case_response, ReadWorkerInviteMessage.Failure):
            return self.http_404_view.get_response()
        view_model = self.presenter.present(use_case_response)
        return redirect(
            url_for(
                "main_member.show_company_work_invite", invite_id=view_model.invite_id
            )
        )
