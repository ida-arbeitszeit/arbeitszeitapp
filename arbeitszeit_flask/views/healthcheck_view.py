from dataclasses import dataclass

import flask


@dataclass
class HealthcheckView:

    def GET(self) -> flask.Response:
        return flask.Response(status=200)
