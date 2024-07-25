from _typeshed import Incomplete

from .config import COOKIE_DURATION as COOKIE_DURATION
from .config import COOKIE_HTTPONLY as COOKIE_HTTPONLY
from .config import COOKIE_NAME as COOKIE_NAME
from .config import COOKIE_SAMESITE as COOKIE_SAMESITE
from .config import COOKIE_SECURE as COOKIE_SECURE
from .config import ID_ATTRIBUTE as ID_ATTRIBUTE
from .config import LOGIN_MESSAGE as LOGIN_MESSAGE
from .config import LOGIN_MESSAGE_CATEGORY as LOGIN_MESSAGE_CATEGORY
from .config import REFRESH_MESSAGE as REFRESH_MESSAGE
from .config import REFRESH_MESSAGE_CATEGORY as REFRESH_MESSAGE_CATEGORY
from .config import SESSION_KEYS as SESSION_KEYS
from .config import USE_SESSION_FOR_NEXT as USE_SESSION_FOR_NEXT
from .mixins import AnonymousUserMixin as AnonymousUserMixin
from .signals import session_protected as session_protected
from .signals import user_accessed as user_accessed
from .signals import user_loaded_from_cookie as user_loaded_from_cookie
from .signals import user_loaded_from_request as user_loaded_from_request
from .signals import user_needs_refresh as user_needs_refresh
from .signals import user_unauthorized as user_unauthorized
from .utils import decode_cookie as decode_cookie
from .utils import encode_cookie as encode_cookie
from .utils import expand_login_view as expand_login_view
from .utils import make_next_param as make_next_param

class LoginManager:
    anonymous_user: Incomplete
    login_view: Incomplete
    blueprint_login_views: Incomplete
    login_message: Incomplete
    login_message_category: Incomplete
    refresh_view: Incomplete
    needs_refresh_message: Incomplete
    needs_refresh_message_category: Incomplete
    session_protection: str
    localize_callback: Incomplete
    unauthorized_callback: Incomplete
    needs_refresh_callback: Incomplete
    id_attribute: Incomplete
    def __init__(
        self, app: Incomplete | None = None, add_context_processor: bool = True
    ) -> None: ...
    def init_app(self, app, add_context_processor: bool = True) -> None: ...
    def unauthorized(self): ...
    def user_loader(self, callback): ...
    @property
    def user_callback(self): ...
    def request_loader(self, callback): ...
    @property
    def request_callback(self): ...
    def unauthorized_handler(self, callback): ...
    def needs_refresh_handler(self, callback): ...
    def needs_refresh(self): ...
