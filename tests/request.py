from typing import Dict, Optional

from arbeitszeit.injector import singleton


@singleton
class FakeRequest:
    def __init__(self) -> None:
        self._args: Dict[str, str] = dict()
        self._form: Dict[str, str] = dict()
        self._json: Dict[str, str] = dict()
        self._environ: Dict[str, str] = dict()

    def query_string(self) -> Dict[str, str]:
        return self._args

    def get_form(self, key: str) -> Optional[str]:
        return self._form.get(key, None)

    def get_header(self, key: str) -> Optional[str]:
        return self._environ.get(key, None)

    def get_json(self, key: str) -> Optional[str]:
        return self._json.get(key, None)

    def set_arg(self, arg: str, value: object) -> None:
        self._args[arg] = str(value)

    def set_form(self, key: str, value: str) -> None:
        self._form[key] = value

    def set_header(self, key: str, value: Optional[str]) -> None:
        if value is None:
            if key in self._environ:
                del self._environ[key]
        else:
            self._environ[key] = value

    def set_json(self, key: str, value: str) -> None:
        self._json[key] = value

    def get_request_target(self) -> str:
        return "/"
