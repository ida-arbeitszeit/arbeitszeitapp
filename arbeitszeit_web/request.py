from __future__ import annotations

from typing import Optional, Protocol


class Request(Protocol):
    def query_string(self) -> QueryString:
        ...

    def get_form(self, key: str) -> Optional[str]:
        ...

    def get_header(self, key: str) -> Optional[str]:
        ...


class QueryString(Protocol):
    def get(self, key: str) -> Optional[str]:
        ...
