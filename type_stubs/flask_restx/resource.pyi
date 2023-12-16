from .model import ModelBase as ModelBase
from .utils import BaseResponse as BaseResponse, unpack as unpack
from _typeshed import Incomplete
from flask.views import MethodView

class Resource(MethodView):
    representations: Incomplete
    method_decorators: Incomplete
    api: Incomplete
    def __init__(self, api: Incomplete | None = ..., *args, **kwargs) -> None: ...
    def dispatch_request(self, *args, **kwargs): ...
    def validate_payload(self, func) -> None: ...
