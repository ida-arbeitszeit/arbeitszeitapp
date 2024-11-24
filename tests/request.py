from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional

from arbeitszeit_web.json import JsonValue


@dataclass
class FakeQueryString:
    values: defaultdict[str, list[str]] = field(
        default_factory=lambda: defaultdict(lambda: list())
    )

    def items(self) -> Iterable[tuple[str, str]]:
        for key in self.values:
            for value in self.values[key]:
                yield key, value

    def get(self, key: str) -> list[str]:
        return self.values.get(key, [])

    def get_last_value(self, key: str) -> str | None:
        match self.values.get(key, []):
            case []:
                return None
            case values:
                return values[-1]

    def append(self, key: str, value: str) -> None:
        self.values[key].append(value)


class FakeRequest:
    def __init__(self, *, query_string: list[tuple[str, str]] | None = None) -> None:
        self._args = FakeQueryString()
        for key, value in query_string or []:
            self._args.append(key, value)
        self._form: Dict[str, str] = dict()
        self._json: JsonValue | None = None
        self._environ: Dict[str, str] = dict()

    def query_string(self) -> FakeQueryString:
        return self._args

    def get_form(self, key: str) -> Optional[str]:
        return self._form.get(key, None)

    def get_header(self, key: str) -> Optional[str]:
        return self._environ.get(key, None)

    def get_json(self) -> JsonValue | None:
        return self._json

    def set_arg(self, arg: str, value: object) -> None:
        self._args.values[arg] = [str(value)]

    def set_form(self, key: str, value: str) -> None:
        self._form[key] = value

    def set_header(self, key: str, value: Optional[str]) -> None:
        if value is None:
            if key in self._environ:
                del self._environ[key]
        else:
            self._environ[key] = value

    def set_json(self, value: JsonValue) -> None:
        self._json = value

    def get_request_target(self) -> str:
        return "/"
