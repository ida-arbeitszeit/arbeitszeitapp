from dataclasses import dataclass

from flask import Response, render_template


@dataclass
class Http409View:
    def get_response(self) -> Response:
        return Response(
            render_template("user/409.html"),
            status=409,
        )
