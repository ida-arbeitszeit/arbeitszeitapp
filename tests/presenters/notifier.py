from typing import List


class NotifierTestImpl:
    def __init__(self) -> None:
        self.warnings: List[str] = []
        self.infos: List[str] = []

    def display_warning(self, text: str) -> None:
        self.warnings.append(text)

    def display_info(self, text: str) -> None:
        self.infos.append(text)
