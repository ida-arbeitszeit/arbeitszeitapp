from _typeshed import Incomplete
from flask.views import MethodView

from .model import ModelBase as ModelBase
from .utils import BaseResponse as BaseResponse
from .utils import unpack as unpack

class Resource(MethodView):
    representations: Incomplete
    method_decorators: Incomplete
    api: Incomplete
    def __init__(self, api=None, *args, **kwargs) -> None: ...
    def dispatch_request(self, *args, **kwargs): ...
    def validate_payload(self, func) -> None: ...
