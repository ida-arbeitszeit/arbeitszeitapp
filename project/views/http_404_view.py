from dataclasses import dataclass

from flask import Response

from arbeitszeit_web.template import TemplateRenderer


@dataclass
class Http404View:
    template: str
    template_renderer: TemplateRenderer

    def get_response(self) -> Response:
        return Response(
            self.template_renderer.render_template(self.template),
            status=404,
        )
