from typing import Protocol


class TextRenderer(Protocol):
    def render_member_registration_message(self, *, confirmation_url: str) -> str:
        ...

    def render_company_registration_message(self, *, confirmation_url: str) -> str:
        ...

    def render_accountant_notification_about_new_plan(
        self, *, product_name: str
    ) -> str:
        ...

    def render_member_notfication_about_work_invitation(self) -> str:
        ...
