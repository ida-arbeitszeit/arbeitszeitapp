from _typeshed import Incomplete

DENY: str
SAMEORIGIN: str
ALLOW_FROM: str
ONE_YEAR_IN_SECS: int
DEFAULT_REFERRER_POLICY: str
DEFAULT_CSP_POLICY: Incomplete
DEFAULT_SESSION_COOKIE_SAMESITE: str
GOOGLE_CSP_POLICY: Incomplete
DEFAULT_PERMISSIONS_POLICY: Incomplete
DEFAULT_DOCUMENT_POLICY: Incomplete
DEFAULT_FEATURE_POLICY: Incomplete
NONCE_LENGTH: int

class Talisman:
    def __init__(self, app=None, **kwargs) -> None: ...
    feature_policy: Incomplete
    permissions_policy: Incomplete
    document_policy: Incomplete
    force_https: Incomplete
    force_https_permanent: Incomplete
    frame_options: Incomplete
    frame_options_allow_from: Incomplete
    strict_transport_security: Incomplete
    strict_transport_security_preload: Incomplete
    strict_transport_security_max_age: Incomplete
    strict_transport_security_include_subdomains: Incomplete
    content_security_policy: Incomplete
    content_security_policy_report_uri: Incomplete
    content_security_policy_report_only: Incomplete
    content_security_policy_nonce_in: Incomplete
    referrer_policy: Incomplete
    session_cookie_secure: Incomplete
    force_file_save: Incomplete
    x_content_type_options: Incomplete
    x_xss_protection: Incomplete
    app: Incomplete
    def init_app(
        self,
        app,
        feature_policy=...,
        permissions_policy=...,
        document_policy=...,
        force_https: bool = True,
        force_https_permanent: bool = False,
        force_file_save: bool = False,
        frame_options=...,
        frame_options_allow_from=None,
        strict_transport_security: bool = True,
        strict_transport_security_preload: bool = False,
        strict_transport_security_max_age=...,
        strict_transport_security_include_subdomains: bool = True,
        content_security_policy=...,
        content_security_policy_report_uri=None,
        content_security_policy_report_only: bool = False,
        content_security_policy_nonce_in=None,
        referrer_policy=...,
        session_cookie_secure: bool = True,
        session_cookie_http_only: bool = True,
        session_cookie_samesite=...,
        x_content_type_options: bool = True,
        x_xss_protection: bool = False,
    ) -> None: ...
    def __call__(self, **kwargs): ...

def get_random_string(length): ...

rnd: Incomplete
