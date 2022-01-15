from dataclasses import dataclass

from flask import Response

from project.template import TemplateIndex, TemplateRenderer


@dataclass
class Http404View:
    template_index: TemplateIndex
    template_renderer: TemplateRenderer

    def get_response(self) -> Response:
        template = self.template_index.get_template_by_name("404")
        return Response(
            self.template_renderer.render_template(template),
            status=404,
        )
