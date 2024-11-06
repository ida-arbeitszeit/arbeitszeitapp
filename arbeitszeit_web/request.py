from __future__ import annotations

from typing import Iterable, Optional, Protocol, Tuple


class Request(Protocol):
    def query_string(self) -> QueryString: ...

    def get_form(self, key: str) -> Optional[str]: ...

    def get_json(self, key: str) -> Optional[str]: ...

    def get_header(self, key: str) -> Optional[str]: ...

    def get_request_target(self) -> str: ...


class QueryString(Protocol):
    def get(self, key: str) -> Optional[str]:
        """Get the value for a particular query arguments."""

    def items(self) -> Iterable[Tuple[str, str]]:
        """Return all query arguments in no particular order."""
