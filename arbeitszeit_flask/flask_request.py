from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from flask import request
from werkzeug.datastructures import MultiDict

from arbeitszeit_web.json import JsonValue


@dataclass
class QueryStringImpl:
    args: MultiDict[str, str]

    def get(self, key: str) -> list[str]:
        return self.args.getlist(key)

    def items(self) -> Iterable[Tuple[str, str]]:
        return self.args.items(multi=True)

    def get_last_value(self, key: str) -> str | None:
        match self.args.getlist(key):
            case []:
                return None
            case values:
                return values[-1]


class FlaskRequest:
    def query_string(self) -> QueryStringImpl:
        return QueryStringImpl(
            args=request.args,
        )

    def get_form(self, key: str) -> Optional[str]:
        return request.form.get(key, None)

    def get_json(self) -> JsonValue | None:
        return request.get_json()

    def get_header(self, key: str) -> Optional[str]:
        return request.headers.get(key, None)

    def get_request_target(self) -> str:
        return request.url
