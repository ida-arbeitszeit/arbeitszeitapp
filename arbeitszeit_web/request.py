from __future__ import annotations

from typing import Iterable, Optional, Protocol, Tuple

from arbeitszeit_web.json import JsonValue


class Request(Protocol):
    def query_string(self) -> QueryString: ...

    def get_form(self, key: str) -> Optional[str]: ...

    def get_json(self) -> JsonValue | None: ...

    def get_header(self, key: str) -> Optional[str]: ...

    def get_request_target(self) -> str: ...


class QueryString(Protocol):
    def get(self, key: str) -> list[str]:
        """Get all values supplied by the client for a given key.

        Example: Calling `r.get('a')` on a request with the query string
            `a=1&a=2` will result in the list `['1', '2']`.
        """

    def items(self) -> Iterable[Tuple[str, str]]:
        """Return all query arguments in no particular order."""

    def get_last_value(self, key: str) -> str | None:
        """Return the last value specified for a given key.

        Example: Given a query string 'a=1&a=2' the call
            `query.get_last_value('a')` must return '2' since it is the
            last value specified for the key 'a'.
        """
