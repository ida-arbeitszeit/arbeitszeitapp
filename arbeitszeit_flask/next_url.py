from typing import Optional
from urllib.parse import urlparse

from flask import session
from is_safe_url import is_safe_url


def save_next_url_in_session(request) -> None:
    hostname = urlparse(request.base_url).hostname
    next = request.args.get("next")
    if next is not None and is_safe_url(next, {hostname}):
        session["next"] = next


def get_next_url_from_session() -> Optional[str]:
    return session.pop("next", None)
