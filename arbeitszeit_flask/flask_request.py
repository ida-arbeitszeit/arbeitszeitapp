from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from flask import request


@dataclass
class QueryStringImpl:
    args: Dict[str, str]

    def get(self, key: str) -> Optional[str]:
        return self.args.get(key)


class FlaskRequest:
    def query_string(self) -> QueryStringImpl:
        return QueryStringImpl(
            args=dict(request.args),
        )

    def get_form(self, key: str) -> Optional[str]:
        return request.form.get(key, None)

    def get_header(self, key: str) -> Optional[str]:
        return request.headers.get(key, None)
