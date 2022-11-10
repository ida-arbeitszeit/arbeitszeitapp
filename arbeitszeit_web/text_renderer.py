from typing import Protocol


class TextRenderer(Protocol):
    def render_member_registration_message(self, *, confirmation_url: str) -> str:
        ...

    def render_company_registration_message(self, *, confirmation_url: str) -> str:
        ...
