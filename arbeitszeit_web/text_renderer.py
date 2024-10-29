from typing import Protocol


class TextRenderer(Protocol):
    def render_member_registration_message(self, *, confirmation_url: str) -> str: ...

    def render_company_registration_message(self, *, confirmation_url: str) -> str: ...

    def render_accountant_notification_about_new_plan(
        self, *, product_name: str, accountant_name: str
    ) -> str: ...

    def render_member_notfication_about_work_invitation(
        self, *, invitation_url: str
    ) -> str: ...

    def render_email_change_warning(
        self, *, admin_email_address: str | None
    ) -> str: ...

    def render_email_change_notification(self, *, change_email_url: str) -> str: ...

    def render_company_notification_about_rejected_plan(
        self, company_name: str, product_name: str, plan_id: str
    ) -> str: ...
