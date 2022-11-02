from typing import Union

import flask
import werkzeug.wrappers.response

Response = Union[flask.Response, werkzeug.wrappers.response.Response, str]
