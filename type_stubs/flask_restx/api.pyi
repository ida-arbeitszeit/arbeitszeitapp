from . import apidoc as apidoc
from ._http import HTTPStatus as HTTPStatus
from .mask import MaskError as MaskError, ParseError as ParseError
from .namespace import Namespace as Namespace
from .postman import PostmanCollectionV1 as PostmanCollectionV1
from .representations import output_json as output_json
from .resource import Resource as Resource
from .swagger import Swagger as Swagger
from .utils import camel_to_dash as camel_to_dash, default_id as default_id, unpack as unpack
from _typeshed import Incomplete

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
    def __init__(self, app: Incomplete | None = ..., version: str = ..., title: Incomplete | None = ..., description: Incomplete | None = ..., terms_url: Incomplete | None = ..., license: Incomplete | None = ..., license_url: Incomplete | None = ..., contact: Incomplete | None = ..., contact_url: Incomplete | None = ..., contact_email: Incomplete | None = ..., authorizations: Incomplete | None = ..., security: Incomplete | None = ..., doc: str = ..., default_id=..., default: str = ..., default_label: str = ..., validate: Incomplete | None = ..., tags: Incomplete | None = ..., prefix: str = ..., ordered: bool = ..., default_mediatype: str = ..., decorators: Incomplete | None = ..., catch_all_404s: bool = ..., serve_challenge_on_401: bool = ..., format_checker: Incomplete | None = ..., url_scheme: Incomplete | None = ..., default_swagger_filename: str = ..., **kwargs) -> None: ...
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
    def add_namespace(self, ns, path: Incomplete | None = ...) -> None: ...
    def namespace(self, *args, **kwargs): ...
    def endpoint(self, name): ...
    @property
    def specs_url(self): ...
    @property
    def base_url(self): ...
    @property
    def base_path(self): ...
    def __schema__(self): ...
    def errorhandler(self, exception): ...
    def owns_endpoint(self, endpoint): ...
    def error_router(self, original_handler, e): ...
    def handle_error(self, e): ...
    def as_postman(self, urlvars: bool = ..., swagger: bool = ...): ...
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