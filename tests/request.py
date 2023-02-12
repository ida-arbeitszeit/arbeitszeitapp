from typing import Dict, Optional, Union

from arbeitszeit.injector import singleton


@singleton
class FakeRequest:
    def __init__(self) -> None:
        self._args: Dict[str, str] = dict()
        self._form: Dict[str, str] = dict()
        self._environ: Dict[str, str] = dict()

    def query_string(self) -> Dict[str, str]:
        return self._args

    def get_form(self, key: str) -> Optional[str]:
        return self._form.get(key, None)

    def get_header(self, key: str) -> Optional[str]:
        return self._environ.get(key, None)

    def set_arg(self, arg: str, value: object) -> None:
        self._args[arg] = str(value)

    def set_form(self, key: str, value: str) -> None:
        self._form[key] = value

    def set_header(self, key: str, value: str) -> None:
        self._environ[key] = value
