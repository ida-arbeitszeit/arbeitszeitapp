from typing import Protocol


class EmailConfiguration(Protocol):
    def get_sender_address(self) -> str:
        ...
