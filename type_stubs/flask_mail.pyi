from collections.abc import Generator

from _typeshed import Incomplete

__version__: str
PY3: Incomplete
PY34: Incomplete
string_types: Incomplete
text_type = str
message_policy: Incomplete

class FlaskMailUnicodeDecodeError(UnicodeDecodeError):
    obj: Incomplete
    def __init__(self, obj, *args) -> None: ...

def force_text(s, encoding: str = "utf-8", errors: str = "strict"): ...
def sanitize_subject(subject, encoding: str = "utf-8"): ...
def sanitize_address(addr, encoding: str = "utf-8"): ...
def sanitize_addresses(addresses, encoding: str = "utf-8"): ...

class Connection:
    mail: Incomplete
    def __init__(self, mail) -> None: ...
    host: Incomplete
    num_emails: int
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
    def configure_host(self): ...
    def send(self, message, envelope_from: Incomplete | None = None) -> None: ...
    def send_message(self, *args, **kwargs) -> None: ...

class BadHeaderError(Exception): ...

class Attachment:
    filename: Incomplete
    content_type: Incomplete
    data: Incomplete
    disposition: Incomplete
    headers: Incomplete
    def __init__(
        self,
        filename: Incomplete | None = None,
        content_type: Incomplete | None = None,
        data: Incomplete | None = None,
        disposition: Incomplete | None = None,
        headers: Incomplete | None = None,
    ) -> None: ...

class Message:
    recipients: Incomplete
    subject: Incomplete
    sender: Incomplete
    reply_to: Incomplete
    cc: Incomplete
    bcc: Incomplete
    body: Incomplete
    html: Incomplete
    date: Incomplete
    msgId: Incomplete
    charset: Incomplete
    extra_headers: Incomplete
    mail_options: Incomplete
    rcpt_options: Incomplete
    attachments: Incomplete
    def __init__(
        self,
        subject: str = "",
        recipients: Incomplete | None = None,
        body: Incomplete | None = None,
        html: Incomplete | None = None,
        sender: Incomplete | None = None,
        cc: Incomplete | None = None,
        bcc: Incomplete | None = None,
        attachments: Incomplete | None = None,
        reply_to: Incomplete | None = None,
        date: Incomplete | None = None,
        charset: Incomplete | None = None,
        extra_headers: Incomplete | None = None,
        mail_options: Incomplete | None = None,
        rcpt_options: Incomplete | None = None,
    ) -> None: ...
    @property
    def send_to(self): ...
    def as_string(self): ...
    def as_bytes(self): ...
    def __bytes__(self) -> bytes: ...
    def has_bad_headers(self): ...
    def is_bad_headers(self): ...
    def send(self, connection) -> None: ...
    def add_recipient(self, recipient) -> None: ...
    def attach(
        self,
        filename: Incomplete | None = None,
        content_type: Incomplete | None = None,
        data: Incomplete | None = None,
        disposition: Incomplete | None = None,
        headers: Incomplete | None = None,
    ) -> None: ...

class _MailMixin:
    def record_messages(self) -> Generator[Incomplete, None, None]: ...
    def send(self, message) -> None: ...
    def send_message(self, *args, **kwargs) -> None: ...
    def connect(self): ...

class _Mail(_MailMixin):
    server: Incomplete
    username: Incomplete
    password: Incomplete
    port: Incomplete
    use_tls: Incomplete
    use_ssl: Incomplete
    default_sender: Incomplete
    debug: Incomplete
    max_emails: Incomplete
    suppress: Incomplete
    ascii_attachments: Incomplete
    def __init__(
        self,
        server,
        username,
        password,
        port,
        use_tls,
        use_ssl,
        default_sender,
        debug,
        max_emails,
        suppress,
        ascii_attachments: bool = False,
    ) -> None: ...

class Mail(_MailMixin):
    app: Incomplete
    state: Incomplete
    def __init__(self, app: Incomplete | None = None) -> None: ...
    def init_mail(self, config, debug: bool = False, testing: bool = False): ...
    def init_app(self, app): ...
    def __getattr__(self, name): ...

signals: Incomplete
email_dispatched: Incomplete
