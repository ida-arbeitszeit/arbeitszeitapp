from _typeshed import Incomplete
from werkzeug.utils import cached_property

from . import apidoc as apidoc
from ._http import HTTPStatus as HTTPStatus
from .mask import MaskError as MaskError
from .mask import ParseError as ParseError
from .namespace import Namespace as Namespace
from .postman import PostmanCollectionV1 as PostmanCollectionV1
from .representations import output_json as output_json
from .resource import Resource as Resource
from .swagger import Swagger as Swagger
from .utils import BaseResponse as BaseResponse
from .utils import camel_to_dash as camel_to_dash
from .utils import default_id as default_id
from .utils import import_check_view_func as import_check_view_func
from .utils import unpack as unpack

endpoint_from_view_func: Incomplete
RE_RULES: Incomplete
HEADERS_BLACKLIST: Incomplete
DEFAULT_REPRESENTATIONS: Incomplete
log: Incomplete

class Api:
    version: Incomplete
    title: Incomplete
    description: Incomplete
    terms_url: Incomplete
    contact: Incomplete
    contact_email: Incomplete
    contact_url: Incomplete
    license: Incomplete
    license_url: Incomplete
    authorizations: Incomplete
    security: Incomplete
    default_id: Incomplete
    ordered: Incomplete
    tags: Incomplete
    error_handlers: Incomplete
    models: Incomplete
    format_checker: Incomplete
    namespaces: Incomplete
    default_swagger_filename: Incomplete
    ns_paths: Incomplete
    representations: Incomplete
    urls: Incomplete
    prefix: Incomplete
    default_mediatype: Incomplete
    decorators: Incomplete
    catch_all_404s: Incomplete
    serve_challenge_on_401: Incomplete
    blueprint_setup: Incomplete
    endpoints: Incomplete
    resources: Incomplete
    app: Incomplete
    blueprint: Incomplete
    default_namespace: Incomplete
    url_scheme: Incomplete
    def __init__(
        self,
        app=None,
        version: str = "1.0",
        title=None,
        description=None,
        terms_url=None,
        license=None,
        license_url=None,
        contact=None,
        contact_url=None,
        contact_email=None,
        authorizations=None,
        security=None,
        doc: str = "/",
        default_id=...,
        default: str = "default",
        default_label: str = "Default namespace",
        validate=None,
        tags=None,
        prefix: str = "",
        ordered: bool = False,
        default_mediatype: str = "application/json",
        decorators=None,
        catch_all_404s: bool = False,
        serve_challenge_on_401: bool = False,
        format_checker=None,
        url_scheme=None,
        default_swagger_filename: str = "swagger.json",
        **kwargs,
    ) -> None: ...
    def init_app(self, app, **kwargs) -> None: ...
    def __getattr__(self, name): ...
    def register_resource(self, namespace, resource, *urls, **kwargs): ...
    def output(self, resource): ...
    def make_response(self, data, *args, **kwargs): ...
    def documentation(self, func): ...
    def render_root(self) -> None: ...
    def render_doc(self): ...
    def default_endpoint(self, resource, namespace): ...
    def get_ns_path(self, ns): ...
    def ns_urls(self, ns, urls): ...
    def add_namespace(self, ns, path=None) -> None: ...
    def namespace(self, *args, **kwargs): ...
    def endpoint(self, name): ...
    @property
    def specs_url(self): ...
    @property
    def base_url(self): ...
    @property
    def base_path(self): ...
    @cached_property
    def __schema__(self): ...
    def errorhandler(self, exception): ...
    def owns_endpoint(self, endpoint): ...
    def error_router(self, original_handler, e): ...
    def handle_error(self, e): ...
    def as_postman(self, urlvars: bool = False, swagger: bool = False): ...
    @property
    def payload(self): ...
    @property
    def refresolver(self): ...
    def mediatypes_method(self): ...
    def mediatypes(self): ...
    def representation(self, mediatype): ...
    def unauthorized(self, response): ...
    def url_for(self, resource, **values): ...

class SwaggerView(Resource):
    def get(self): ...
    def mediatypes(self): ...

def mask_parse_error_handler(error): ...
def mask_error_handler(error): ...
