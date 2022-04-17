from typing import Dict, Protocol


class Colors(Protocol):
    @property
    def primary(self) -> str:
        ...

    @property
    def info(self) -> str:
        ...

    @property
    def warning(self) -> str:
        ...

    @property
    def danger(self) -> str:
        ...

    @property
    def success(self) -> str:
        ...

    def get_dict(self) -> Dict[str, str]:
        ...
