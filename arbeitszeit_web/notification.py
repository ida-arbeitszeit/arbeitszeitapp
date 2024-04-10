from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    def display_warning(self, text: str) -> None: ...

    def display_info(self, text: str) -> None: ...
