from dataclasses import dataclass
from uuid import UUID

from flask import Response

from arbeitszeit.use_cases import ReadMessage, ReadMessageFailure
from arbeitszeit_web.read_message import ReadMessageController, ReadMessagePresenter
from arbeitszeit_web.template import TemplateRenderer

from .http_404_view import Http404View


@dataclass
class ReadMessageView:
    read_message: ReadMessage
    controller: ReadMessageController
    presenter: ReadMessagePresenter
    template_renderer: TemplateRenderer
    template_name: str
    http_404_view: Http404View

    def respond_to_get(self, message_id: UUID) -> Response:
        use_case_request = self.controller.process_request_data(message_id)
        use_case_response = self.read_message(use_case_request)
        if isinstance(use_case_response, ReadMessageFailure):
            return self.http_404_view.get_response()
        view_model = self.presenter.present(use_case_response)
        content = self.template_renderer.render_template(
            self.template_name, context=dict(view_model=view_model)
        )
        return Response(content)
