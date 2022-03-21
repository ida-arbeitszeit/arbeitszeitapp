from typing import Optional, Protocol


class Request(Protocol):
    def get_arg(self, arg: str) -> Optional[str]:
        ...

    def get_form(self, key: str) -> Optional[str]:
        ...

    def get_environ(self, key: str) -> Optional[str]:
        ...
