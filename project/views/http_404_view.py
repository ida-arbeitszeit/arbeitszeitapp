from dataclasses import dataclass

from flask import Response, render_template


@dataclass
class Http404View:
    template: str

    def get_response(self) -> Response:
        return Response(
            render_template(self.template),
            status=404,
        )
