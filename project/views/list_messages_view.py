from dataclasses import dataclass

from flask import Response

from arbeitszeit.use_cases import ListMessages
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from project.template import TemplateRenderer

from .http_404_view import Http404View


@dataclass
class ListMessagesView:
    list_messages: ListMessages
    controller: ListMessagesController
    presenter: ListMessagesPresenter
    not_found_view: Http404View
    template_name: str
    template_renderer: TemplateRenderer

    def respond_to_get(self) -> Response:
        use_case_request = self.controller.process_request_data()
        if use_case_request is None:
            return self.not_found_view.get_response()
        use_case_response = self.list_messages(use_case_request)
        view_model = self.presenter.present(use_case_response)
        return Response(
            self.template_renderer.render_template(
                self.template_name,
                context=dict(
                    view_model=view_model,
                ),
            )
        )
