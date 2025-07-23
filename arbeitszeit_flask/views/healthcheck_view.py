from dataclasses import dataclass

import flask


@dataclass
class HealthcheckView:
    """Simple endpoint that returns 200 OK to indicate the application is running.
    Used by Docker healthchecks and deployment tests.
    """

    def GET(self) -> flask.Response:
        """Return 200 OK to indicate the application is running."""
        return flask.Response(status=200)
