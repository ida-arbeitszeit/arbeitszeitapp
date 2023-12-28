from dataclasses import dataclass

from flask import Response, render_template


@dataclass
class Http403View:
    def get_response(self) -> Response:
        return Response(
            render_template("user/403.html"),
            status=403,
        )
