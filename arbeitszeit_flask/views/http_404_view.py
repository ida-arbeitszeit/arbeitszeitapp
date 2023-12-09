from dataclasses import dataclass

from flask import Response, render_template


@dataclass
class Http404View:
    def get_response(self) -> Response:
        return Response(
            render_template("user/404.html"),
            status=404,
        )
